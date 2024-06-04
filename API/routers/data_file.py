from fastapi import APIRouter
from fastapi.responses import FileResponse

from services import file_management

router = APIRouter(prefix="/files")

@router.get("/")
def get_all_file(type: str = None):
    return file_management.getAllFile(type)

@router.get("/download")
def download(id: str = None):
    path = "./data/tgdt_categories.csv"  # Đường dẫn tới file của bạn
    return FileResponse(path, filename="tgdt_categories.csv")