import os
import aiofiles
from fastapi import UploadFile
from .interface import IFileStorage

class LocalFileStorage(IFileStorage):
    def __init__(self, base_path: str, base_url: str):
        self.base_path = base_path
        self.base_url = base_url
        os.makedirs(self.base_path, exist_ok=True)

    async def save(self, file: UploadFile, path: str, filename: str) -> str:
        full_dir = os.path.join(self.base_path, path)
        os.makedirs(full_dir, exist_ok=True)
        full_path = os.path.join(full_dir, filename)
        
        try:
            async with aiofiles.open(full_path, "wb") as f:
                while content := await file.read(1024 * 1024):  # Read in 1MB chunks
                    await f.write(content)
        finally:
            await file.close()

        relative_path = os.path.join(path, filename)
        return str(relative_path).replace("\\", "/") # Ensure forward slashes for URLs

    async def delete(self, file_path: str) -> None:
        if not file_path:
            return
        full_path = os.path.join(self.base_path, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    def get_public_url(self, file_path: str) -> str:
        return f"{self.base_url}/{file_path}"