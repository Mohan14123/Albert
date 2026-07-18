class BaseAppException(Exception):
    """Base class for all custom application exceptions."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(BaseAppException):
    """Raised when authentication fails (invalid credentials, bad token, etc.)."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(BaseAppException):
    """Raised when the user does not have permission to access a resource."""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)


class NotFoundError(BaseAppException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(BaseAppException):
    """Raised when a request contains invalid data or violates business logic."""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=400)


class RateLimitedError(BaseAppException):
    """Raised when a user exceeds their rate limit."""
    def __init__(self, message: str = "Too many requests"):
        super().__init__(message, status_code=429)


class ProviderError(BaseAppException):
    """Raised when a third-party AI provider encounters an error."""
    def __init__(self, message: str = "Provider error occurred"):
        super().__init__(message, status_code=502)
