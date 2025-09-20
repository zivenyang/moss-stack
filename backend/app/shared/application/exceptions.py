class ApplicationError(Exception):
    """Base class for exceptions in the application layer."""
    pass

class AuthorizationError(ApplicationError):
    """Raised when a user is not authorized to perform an action."""
    pass

class InvalidCommandError(ApplicationError):
    """Raised when a command is invalid or contains invalid data."""
    pass

class ResourceNotFoundError(ApplicationError):
    """A more generic not-found error for the application layer."""
    pass