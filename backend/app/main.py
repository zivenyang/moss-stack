from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio

from app.config import settings
from app.shared.web.middleware import (
    ExceptionHandlingMiddleware,
    LoggingContextMiddleware,
)
from app.di import initialize_dependencies
from app.router import autodiscover_and_include_routers
from app.shared.infrastructure.logging.config import setup_logging
from app.workers.main import run_kafka_consumer_in_background

# --- 1. 日志系统优先初始化 ---
setup_logging()

# --- 2. 应用生命周期管理 (Lifespan) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    print("--- 🚀 Application Starting Up... ---")
    
    # a. 启动后台的 Kafka 消费者任务
    consumer_task = asyncio.create_task(run_kafka_consumer_in_background(app.container))
    app.state.consumer_task = consumer_task # 将任务存储在app.state以便关闭时访问
    
    yield
    
    # b. 应用关闭逻辑
    print("--- 🔌 Application Shutting Down... ---")
    if hasattr(app.state, "consumer_task") and not app.state.consumer_task.done():
        app.state.consumer_task.cancel()
        try:
            await app.state.consumer_task
        except asyncio.CancelledError:
            print("--- Kafka consumer task cancelled successfully. ---")


# --- 3. 应用创建工厂函数 ---
def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application and its dependencies.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        lifespan=lifespan,
    )

    # a. 初始化依赖注入容器、事件订阅
    initialize_dependencies(app, main_module_name=__name__)
    
    # b. 添加中间件 (顺序很重要)
    app.add_middleware(LoggingContextMiddleware)
    app.add_middleware(ExceptionHandlingMiddleware)
    
    # c. 挂载静态文件目录
    app.mount(
        settings.STATIC_URL,
        StaticFiles(directory=settings.STATIC_FILES_PATH),
        name="static",
    )

    # d. 自动发现、注册路由，并为依赖注入准备模块列表
    router_modules = autodiscover_and_include_routers(app, "app.features")
    app.container.wire(modules=[__name__] + router_modules)

    return app

# --- 4. 创建应用实例 ---
app = create_app()

# --- 5. 添加顶层/非业务路由 ---
@app.get("/health", tags=["Health Check"])
async def health_check():
    """Verifies that the application is running."""
    return {"status": "ok"}