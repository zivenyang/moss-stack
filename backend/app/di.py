from fastapi import FastAPI
from app.container import AppContainer
from app.config import settings

# --- [新增] 导入事件和处理器以进行连接 ---
from app.shared.infrastructure.bus.event import IEventBus
from app.features.iam.domain.events import UserRegistered
from app.features.iam.application.event_handlers import IamEventHandlers

# --- [新增] 导入所有需要被 "wire" 的路由模块 ---
from app.features.iam.api import auth_router, user_router, admin_router
from app.features.item.api import user_router as item_user_router
from app.features.item.api import admin_router as item_admin_router
# ... import future routers here

# A list of all modules where dependency injection needs to be applied.
_ROUTERS_TO_WIRE = [
    auth_router,
    user_router,
    admin_router,
    item_user_router,
    item_admin_router,
]


def _wire_dependencies(container: AppContainer, main_module_name: str):
    """
    Wires the container to all modules that use dependency injection.
    """
    # The main module (`main.py`) also needs to be wired for health checks etc.
    container.wire(modules=[main_module_name] + _ROUTERS_TO_WIRE)


def _subscribe_event_handlers(container: AppContainer):
    """
    Instantiates all event handler classes and subscribes them to the event bus.
    This is now the single place to manage event subscriptions.
    """
    event_bus: IEventBus = container.event_bus()

    # --- 2. 在这里实例化具体的处理器 ---
    #    这些处理器现在是 "ad-hoc" 实例，而不是由容器管理的 provider
    iam_handlers = IamEventHandlers()
    # item_handlers = ItemEventHandlers()

    # --- 3. 执行订阅 ---
    event_bus.subscribe(UserRegistered, iam_handlers.send_welcome_email)
    # item_handlers = container.item_event_handlers()
    # event_bus.subscribe(ItemCreated, item_handlers.handle_item_creation)


def initialize_dependencies(app: FastAPI, main_module_name: str = "app.main"):
    """
    The main entry point for setting up the application's dependency injection.

    - Creates the container.
    - Wires dependencies to modules.
    - Subscribes event handlers.
    - Attaches the container to the FastAPI app instance.
    """
    # 1. Create and configure the container
    container = AppContainer()
    container.config.from_dict(settings.model_dump())

    # 2. Subscribe event handlers
    _subscribe_event_handlers(container)

    # 3. Wire the container to the FastAPI app and its routers
    _wire_dependencies(container, main_module_name)

    # 4. Attach the container to the app for access in lifespan, etc.
    app.container = container
