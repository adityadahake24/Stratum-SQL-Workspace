import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


class StratumException(Exception):
    def __init__(self, message: str, code: str = "error", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(StratumException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", code="not_found", status_code=404)


class UnauthorizedError(StratumException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, code="unauthorized", status_code=401)


class ForbiddenError(StratumException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, code="forbidden", status_code=403)


class ConnectionError(StratumException):
    def __init__(self, message: str):
        super().__init__(message, code="connection_error", status_code=400)


class QueryError(StratumException):
    def __init__(self, message: str, pg_code: str = None):
        super().__init__(message, code="query_error", status_code=422)
        self.pg_code = pg_code


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(StratumException)
    async def stratum_exception_handler(request: Request, exc: StratumException):
        logger.warning("stratum_exception", code=exc.code, message=exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.code, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", error=str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred"},
        )
