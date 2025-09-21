import abc
from fastapi import UploadFile

class IFileStorage(abc.ABC):
    @abc.abstractmethod
    async def save(self, file: UploadFile, path: str, filename: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, file_path: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_public_url(self, file_path: str) -> str:
        raise NotImplementedError