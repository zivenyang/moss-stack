from pydantic import BaseModel


class ValueObject(BaseModel):
    """
    Base class for value objects in the domain layer.
    Value objects are defined by their attributes rather than a unique ID.
    They should be treated as immutable.
    """

    class Config:
        frozen = True  # Make instances immutable
        from_attributes = True
