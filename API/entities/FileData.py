from pydantic import BaseModel


class FileData(BaseModel):
    name: str
    dir: str
    size: str