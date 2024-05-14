from fastapi import APIRouter, HTTPException

from database.mysql_connector import initialTable


router = APIRouter(prefix="/db")

@router.get("/init")
def createTable():
    initialTable()
    return "_____Initial Database Successfully______"