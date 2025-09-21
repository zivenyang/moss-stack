from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.shared.infrastructure.db.session import async_engine
from app.features.iam.api.auth_router import router as auth_router
from app.features.iam.api.user_router import router as user_router
from app.features.iam.api.admin_router import router as admin_user_router
from app.features.item.api.user_router import router as item_user_router 
from app.features.item.api.admin_router import router as item_admin_router 
from app.shared.web.middleware import ExceptionHandlingMiddleware, LoggingContextMiddleware 
from app.shared.infrastructure.logging.config import setup_logging

# --- 生命周期事件 (Lifespan Events) ---
# 推荐使用 lifespan 而不是旧的 @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    setup_logging()
    print("--- Starting up Application ---")
    # 这里可以添加一些启动时检查，比如尝试连接数据库
    yield
    # Shutdown logic
    print("--- Shutting down Application ---")
    await async_engine.dispose()

# --- 创建 FastAPI 应用实例 ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    # You can add other metadata like version, description, etc.
)

# --- 健康检查端点 ---
@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}

# --- 包含功能模块的路由 ---
app.include_router(auth_router, prefix=settings.API_V1_STR, tags=["IAM - Authentication"])
app.include_router(user_router, prefix=f"{settings.API_V1_STR}/users", tags=["IAM - Users"])
app.include_router(admin_user_router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["IAM - Admin"])

app.include_router(item_user_router, prefix=f"{settings.API_V1_STR}/items", tags=["Items"])
app.include_router(item_admin_router, prefix=f"{settings.API_V1_STR}/admin/items", tags=["Admin - Items"])
# --- 添加全局中间件 ---
app.add_middleware(ExceptionHandlingMiddleware)
app.add_middleware(LoggingContextMiddleware)