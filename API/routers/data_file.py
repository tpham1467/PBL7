from fastapi import APIRouter

from services import file_management

router = APIRouter(prefix="/files")

@router.get("/")
def get_all_file(type: str = None):
    return file_management.getAllFile(type)

@router.get("/download")
def download(id: str = None):
    return f"hehe {id}"