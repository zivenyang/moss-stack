from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.config import settings
from app.shared.web.middleware import (
    ExceptionHandlingMiddleware,
    LoggingContextMiddleware,
)
from app.di import initialize_dependencies
from app.router import autodiscover_and_include_routers
from app.shared.infrastructure.logging.config import setup_logging

def create_app() -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup logic
        # You can run the Kafka consumer here if needed
        setup_logging() 
        yield
        # Shutdown logic
    
    app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

    # 1. 初始化所有依赖注入和事件订阅
    #    We pass `__name__` which is 'app.main' so the wiring knows about this module.
    initialize_dependencies(app, main_module_name=__name__)
    
    # 2. 添加中间件
    app.add_middleware(LoggingContextMiddleware)
    app.add_middleware(ExceptionHandlingMiddleware)

    # 3. 自动发现并注册所有路由
    autodiscover_and_include_routers(app, "app.features")
    
    app.mount(
    settings.STATIC_URL,
    StaticFiles(directory=settings.STATIC_FILES_PATH),
    name="static",
    )

    return app

# --- 创建应用实例 ---
app = create_app()

# --- 健康检查端点 ---
@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}


