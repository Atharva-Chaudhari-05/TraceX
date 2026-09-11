import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.context import get_request_id

logger = logging.getLogger(__name__)


def build_error_response(code: str, message: str, status_code: int, headers: dict | None = None) -> JSONResponse:
    content = {
        "error": {
            "code": code,
            "message": message,
            "request_id": get_request_id()
        }
    }
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = "HTTP_ERROR"
    if exc.status_code == status.HTTP_400_BAD_REQUEST:
        code = "BAD_REQUEST"
    elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
        code = "UNAUTHORIZED"
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        code = "FORBIDDEN"
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        code = "NOT_FOUND"

    headers = getattr(exc, "headers", None)
    return build_error_response(
        code=code,
        message=str(exc.detail),
        status_code=exc.status_code,
        headers=headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return build_error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected server error: {str(exc)}", exc_info=True)
    return build_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def setup_exception_handlers(app):
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(500, global_exception_handler)
