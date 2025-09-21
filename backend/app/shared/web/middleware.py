from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.shared.domain.exceptions import (
    DomainError,
    BusinessRuleViolationError,
    AggregateNotFoundError,
)
from app.shared.application.exceptions import (
    ApplicationError,
    AuthorizationError,
    ResourceNotFoundError,
)

import uuid
import time
import structlog
from starlette.middleware.base import RequestResponseEndpoint


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except BusinessRuleViolationError as e:
            return JSONResponse(status_code=400, content={"detail": e.message})
        except (AggregateNotFoundError, ResourceNotFoundError) as e:
            return JSONResponse(
                status_code=404, content={"detail": str(e) or "Resource not found"}
            )
        except AuthorizationError as e:
            return JSONResponse(
                status_code=403, content={"detail": str(e) or "Forbidden"}
            )
        except DomainError as e:
            return JSONResponse(
                status_code=409, content={"detail": f"Conflict: {e}"}
            )  # 409 Conflict
        except ApplicationError as e:
            return JSONResponse(
                status_code=422, content={"detail": f"Unprocessable Entity: {e}"}
            )  # 422 Unprocessable
        except Exception as e:
            # Log the full exception traceback here for debugging
            # logger.exception("An unexpected error occurred")
            return JSONResponse(
                status_code=500,
                content={"detail": f"An internal server error occurred: {e}"},
            )


class LoggingContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 清除上一个请求可能残留的上下文
        structlog.contextvars.clear_contextvars()

        # 为当前请求绑定上下文信息
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            client_ip=request.client.host if request.client else "unknown",
        )

        start_time = time.time()

        # 在返回的响应头中添加 request_id，方便前端或客户端追踪
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        process_time = time.time() - start_time

        # 记录请求完成的日志
        logger = structlog.get_logger("api.access")
        logger.info(
            "Request completed",
            status_code=response.status_code,
            process_time=round(process_time, 4),
        )

        return response
