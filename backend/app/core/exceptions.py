"""Custom exceptions and their HTTP mapping."""


class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ProviderNotConfiguredError(AppError):
    status_code = 503
    code = "provider_not_configured"


class ProviderError(AppError):
    status_code = 502
    code = "provider_error"


class ProviderTimeoutError(ProviderError):
    status_code = 504
    code = "provider_timeout"


class ProviderRateLimitError(ProviderError):
    status_code = 429
    code = "provider_rate_limited"


class InvalidProviderResponseError(ProviderError):
    code = "invalid_provider_response"


class ProtocolPendingError(AppError):
    """Raised for features that need the official competition protocol."""
    status_code = 501
    code = "protocol_pending"
