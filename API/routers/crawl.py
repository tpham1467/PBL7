#lib
from fastapi import APIRouter, HTTPException
from redis import Redis
from redis.lock import Lock as RedisLock
from celery.result import AsyncResult
import task
# entities
from entities import TaskOut

from task import crawl_category

router = APIRouter(prefix="/crawl")

redis_instance = Redis.from_url(task.redis_url)
lock = RedisLock(redis_instance, name="task_id")
REDIS_TASK_KEY = "current_task"

@router.get("/category-tgdd")
def crawl_category_tgdd() -> TaskOut:
    try:
        if not lock.acquire(blocking_timeout=4):
            raise HTTPException(status_code=500, detail="Could not acquire lock")

        task_id = redis_instance.get(REDIS_TASK_KEY)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            r = crawl_category.delay()
            redis_instance.set(REDIS_TASK_KEY, r.task_id)
            return _to_task_out(r)
        else:
            # the last task is still running!
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        lock.release()

def _to_task_out(r: AsyncResult) -> TaskOut:
    return TaskOut(id=r.task_id, status=r.status)