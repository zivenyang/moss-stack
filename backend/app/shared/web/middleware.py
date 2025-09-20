from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.shared.domain.exceptions import DomainError, BusinessRuleViolationError, AggregateNotFoundError
from app.shared.application.exceptions import ApplicationError, AuthorizationError, ResourceNotFoundError

class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except BusinessRuleViolationError as e:
            return JSONResponse(status_code=400, content={"detail": e.message})
        except (AggregateNotFoundError, ResourceNotFoundError) as e:
            return JSONResponse(status_code=404, content={"detail": str(e) or "Resource not found"})
        except AuthorizationError as e:
            return JSONResponse(status_code=403, content={"detail": str(e) or "Forbidden"})
        except DomainError as e:
            return JSONResponse(status_code=409, content={"detail": f"Conflict: {e}"}) # 409 Conflict
        except ApplicationError as e:
            return JSONResponse(status_code=422, content={"detail": f"Unprocessable Entity: {e}"}) # 422 Unprocessable
        except Exception as e:
            # Log the full exception traceback here for debugging
            # logger.exception("An unexpected error occurred")
            return JSONResponse(
                status_code=500,
                content={"detail": "An internal server error occurred."}
            )