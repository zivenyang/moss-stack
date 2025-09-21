import logging
import sys
import structlog
from app.config import settings


def setup_logging():
    """
    Set up structured logging for the application.
    This configuration uses structlog to create JSON-formatted logs,
    which are ideal for production environments and log aggregation systems.
    """
    # 1. 配置Python标准logging
    # --------------------------
    # 这是structlog处理链的基础
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,  # 设置一个基础级别
    )

    # 2. 配置structlog的处理链 (processors)
    # ------------------------------------
    # 这是日志记录从产生到输出所经过的一系列处理步骤
    shared_processors = [
        # 添加日志级别、时间戳等上下文信息
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.LOG_FORMAT == "json":
        # 生产环境使用的JSON格式化处理器
        processors = shared_processors + [
            # 将事件字典扁平化
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # 开发环境使用的彩色控制台格式化处理器
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]

    # 3. 整合structlog与标准logging
    # -------------------------------
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 4. (可选但推荐) 拦截标准库日志
    # ---------------------------------
    # 让所有通过标准logging库产生的日志（如来自第三方库的日志）
    # 也经过structlog的处理链，从而实现格式统一
    # from structlog.stdlib import install_to_standard_library
    # install_to_standard_library()


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a pre-configured logger instance.
    """
    return structlog.get_logger(name)
