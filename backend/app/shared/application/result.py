from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")
E = TypeVar("E", bound=Exception)

class Result(BaseModel, Generic[T, E]):
    """

    A standardized result object for application layer services.
    It encapsulates either a successful value or an error.
    This helps to avoid raising exceptions for predictable business failures
    and makes the control flow more explicit.
    """
    is_success: bool
    value: Optional[T] = None
    error: Optional[E] = None

    @classmethod
    def success(cls, value: T) -> "Result[T, Any]":
        return cls(is_success=True, value=value)

    @classmethod
    def failure(cls, error: E) -> "Result[Any, E]":
        return cls(is_success=False, error=error)

    def get_value(self) -> T:
        """Returns the value if the result is a success, otherwise raises the error."""
        if not self.is_success or self.value is None:
            # The type checker won't know self.error is not None here,
            # but our logic ensures it is.
            raise self.error or Exception("Unknown error in Result.failure")
        return self.value