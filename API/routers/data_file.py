import os

from fastapi import APIRouter
from fastapi.responses import FileResponse
from services import file_management

router = APIRouter(prefix="/files")


@router.get("/")
def get_all_file(type: str = None):
    return file_management.getAllFile(type)


@router.get("/download")
def download(name: str):
    file = file_management.get_file_by_name(name)
    if not os.path.isfile(file.dir):
        return f"The file '{file.name}' does not exist."

    return FileResponse(
        file.dir, filename=file_management.process_data_file_name(file.dir)
    )
