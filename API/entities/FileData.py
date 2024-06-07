import time
from pydantic import BaseModel


class FileData:
    def __init__ (self, name, dir, size, create_at = time.localtime()):
        self.name = name
        self.dir = dir
        self.size = size
        self.create_at = create_at