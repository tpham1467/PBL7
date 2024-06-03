# lib
from fastapi import APIRouter
from fastapi import APIRouter, HTTPException
from redis import Redis
from redis.lock import Lock as RedisLock
from celery.result import AsyncResult
import config
import task

from entities import TaskOut
# entities
redis_instance = Redis.from_url(task.redis_url)
router = APIRouter(prefix="/tracking")

@router.get('/')
def tracking():
    task_keys = list(config.__TASK_KEY__.values())
    tasks = []
    for task_key in task_keys:
        task_id = redis_instance.get(task_key)
        task_object = task.app.AsyncResult(task_key)
        if task_object is not None: 
            tasks.append({'id': task_id, 'name': task_key, 'state': task_object.state})

    return tasks

def _to_task_out(r: AsyncResult) -> TaskOut:
    return TaskOut(id=r.task_id, status=r.status)