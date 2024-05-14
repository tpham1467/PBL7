from fastapi import APIRouter

from services import cli
from entities.Command import CommandRequest

router = APIRouter(prefix="/cli")

@router.post("/execute")
async def execute_cli(commandRequest: CommandRequest):
    return cli.execute_cli(commandRequest)

