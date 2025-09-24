import abc
from typing import TypeVar, Generic

# Define generic types for commands, queries, and their results
CommandT = TypeVar("CommandT")
QueryT = TypeVar("QueryT")
ResultT = TypeVar("ResultT")

class ICommandHandler(abc.ABC, Generic[CommandT, ResultT]):
    """Interface for command handlers."""
    @abc.abstractmethod
    async def handle(self, command: CommandT) -> ResultT:
        raise NotImplementedError

class IQueryHandler(abc.ABC, Generic[QueryT, ResultT]):
    """Interface for query handlers."""
    @abc.abstractmethod
    async def handle(self, query: QueryT) -> ResultT:
        raise NotImplementedError