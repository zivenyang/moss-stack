from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field
import math

DataT = TypeVar("DataT")

class PageParams(BaseModel):
    """
    Pydantic model for pagination query parameters (page and size).
    Provides default values and validation.
    """
    page: int = Field(1, ge=1, description="Page number, starting from 1")
    size: int = Field(10, gt=0, le=100, description="Number of items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

class Paginated(BaseModel, Generic[DataT]):
    """
    A generic paginated response model.
    """
    items: List[DataT]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: List[DataT], total: int, params: PageParams) -> "Paginated[DataT]":
        return cls(
            items=items,
            total=total,
            page=params.page,
            size=params.size,
            pages=math.ceil(total / params.size) if params.size > 0 else 0,
        )