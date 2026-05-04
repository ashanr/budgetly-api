from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class BudgetlyException(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400, details: list = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


class AuthenticationError(BudgetlyException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR", status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(BudgetlyException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "AUTHORIZATION_ERROR", status.HTTP_403_FORBIDDEN)


class NotFoundError(BudgetlyException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", "NOT_FOUND", status.HTTP_404_NOT_FOUND)


class ValidationError(BudgetlyException):
    def __init__(self, message: str = "Validation failed", details: list = None):
        super().__init__(message, "VALIDATION_ERROR", status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class RateLimitError(BudgetlyException):
    def __init__(self):
        super().__init__("Rate limit exceeded", "RATE_LIMIT_ERROR", status.HTTP_429_TOO_MANY_REQUESTS)


def _error_response(request: Request, status_code: int, message: str, code: str, details: list = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "data": None,
            "meta": None,
            "error": {
                "code": code,
                "details": details or [],
            },
        },
    )


async def budgetly_exception_handler(request: Request, exc: BudgetlyException) -> JSONResponse:
    return _error_response(request, exc.status_code, exc.message, exc.code, exc.details)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [{"field": ".".join(str(l) for l in e["loc"]), "message": e["msg"]} for e in exc.errors()]
    return _error_response(request, status.HTTP_422_UNPROCESSABLE_ENTITY, "Validation failed", "VALIDATION_ERROR", details)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return _error_response(request, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error", "INTERNAL_ERROR")
