#lib
from fastapi import APIRouter, HTTPException
from redis import Redis
from redis.lock import Lock as RedisLock
from celery.result import AsyncResult
from database.mysql_connector import update_jobs_by_task_id, update_jobs
import config
import task
# entities
from entities import TaskOut

from task import preprocess_data

router = APIRouter(prefix="/preprocess")

redis_instance = Redis.from_url(task.redis_url)
lock = RedisLock(redis_instance, name="task_id")

@router.get("/start")
def start_preprocess() -> TaskOut:
    try:
        if not lock.acquire(blocking_timeout=4):
            raise HTTPException(status_code=500, detail="Could not acquire lock")

        task_id = redis_instance.get(config.__TASK_KEY__['preprocess'])
        print(task_id)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            update_jobs(task_key=config.__TASK_KEY__['preprocess'], status='PENDING')
            r = preprocess_data.delay()
            redis_instance.set(config.__TASK_KEY__['preprocess'], r.task_id)
            return _to_task_out(r, config.__TASK_KEY__['preprocess'])
        else:
            # the last task is still running!
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        lock.release()
        
def _to_task_out(r: AsyncResult, type: str) -> TaskOut:
    print("Update Task into DB...")
    update_jobs_by_task_id(type, task_id=r.task_id)
    return TaskOut(id=r.task_id, status=r.status)