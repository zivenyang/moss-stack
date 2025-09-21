class DomainError(Exception):
    """Base class for exceptions in the domain layer."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class BusinessRuleViolationError(DomainError):
    """
    Raised when a business rule is violated.
    This is a key exception to signal that an operation cannot be completed
    because it would break a domain invariant.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class AggregateNotFoundError(DomainError):
    """Raised when an aggregate root cannot be found in a repository."""

    pass
