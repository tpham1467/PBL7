# lib
from datetime import datetime
from fastapi import APIRouter
from fastapi import APIRouter, HTTPException
from redis import Redis
from redis.lock import Lock as RedisLock
from celery.result import AsyncResult
from database.mysql_connector import checkMysqlConnect, getAll, insert
import task
# entities
from entities import TaskOut

from task import dummy_task

router = APIRouter(prefix="/test")

redis_instance = Redis.from_url(task.redis_url)
lock = RedisLock(redis_instance, name="task_id")
REDIS_TASK_KEY = "current_task"

@router.get("/call", response_description="Test API")
async def index():
    print(insert("file_data", name="category", dir="./crawl", size="16 KB", created_at=datetime.now()))
    print("Test API")
    return "PBL7 API Test"

@router.get("/start")
def start() -> TaskOut:
    try:
        if not lock.acquire(blocking_timeout=4):
            raise HTTPException(status_code=500, detail="Could not acquire lock")

        task_id = redis_instance.get(REDIS_TASK_KEY)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            r = dummy_task.delay()
            print(f"{r.task_id}")
            redis_instance.set(REDIS_TASK_KEY, r.task_id)
            return _to_task_out(r)
        else:
            # the last task is still running!
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        lock.release()

@router.get("/status")
def status(task_id: str = None) -> TaskOut:
    task_id = task_id or redis_instance.get(REDIS_TASK_KEY)
    if task_id is None:
        raise HTTPException(
            status_code=400, detail=f"Could not determine task {task_id}"
        )
    r = task.app.AsyncResult(task_id)
    return _to_task_out(r)

def _to_task_out(r: AsyncResult) -> TaskOut:
    return TaskOut(id=r.task_id, status=r.status)