from typing import Any


class AppError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        error_code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}

    @classmethod
    def bad_request(cls, error_code: str, message: str, details: dict[str, Any] | None = None) -> "AppError":
        return cls(status_code=400, error_code=error_code, message=message, details=details)

    @classmethod
    def not_found(cls, error_code: str, message: str, details: dict[str, Any] | None = None) -> "AppError":
        return cls(status_code=404, error_code=error_code, message=message, details=details)

    @classmethod
    def conflict(cls, error_code: str, message: str, details: dict[str, Any] | None = None) -> "AppError":
        return cls(status_code=409, error_code=error_code, message=message, details=details)
