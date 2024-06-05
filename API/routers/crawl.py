#lib
from fastapi import APIRouter, HTTPException
from redis import Redis
from redis.lock import Lock as RedisLock
from celery.result import AsyncResult
from database.mysql_connector import update_jobs_by_task_id, update_jobs
import task
# entities
from entities import TaskOut

from task import crawl_category_task, test_sleep, crawl_description, crawl_end_page_link_category, crawl_product_link
import config

router = APIRouter(prefix="/crawl")

redis_instance = Redis.from_url(task.redis_url)
lock = RedisLock(redis_instance, name="task_id")

@router.get("/category-tgdd")
def crawl_category_tgdd() -> TaskOut:
    try:
        if not lock.acquire(blocking_timeout=4):
            raise HTTPException(status_code=500, detail="Could not acquire lock")

        task_id = redis_instance.get(config.__TASK_KEY__['tgdd_crawl_category'])
        print(task_id)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            update_jobs(task_key=config.__TASK_KEY__['tgdd_crawl_category'], status='PENDING')
            r = crawl_category_task.delay()
            redis_instance.set(config.__TASK_KEY__['tgdd_crawl_category'], r.task_id)
            return _to_task_out(r, config.__TASK_KEY__['tgdd_crawl_category'])
        else:
            # the last task is still running!
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        lock.release()

@router.get("/end-page-link-tgdd")
def crawl_end_page_tgdd() -> TaskOut:
    try:
        if not lock.acquire(blocking_timeout=4):
            raise HTTPException(status_code=500, detail="Could not acquire lock")

        task_id = redis_instance.get(config.__TASK_KEY__['tgdd_crawl_end_page_link'])
        print(task_id)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            update_jobs(task_key=config.__TASK_KEY__['tgdd_crawl_end_page_link'], status='PENDING')
            r = crawl_end_page_link_category.delay()
            redis_instance.set(config.__TASK_KEY__['tgdd_crawl_end_page_link'], r.task_id)
            return _to_task_out(r, config.__TASK_KEY__['tgdd_crawl_end_page_link'])
        else:
            # the last task is still running!
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        lock.release()

@router.get('/product-link-tgdd')
def crawl_product_tgdd() -> TaskOut:
    try:
        if not lock.acquire(blocking_timeout=4):
            raise HTTPException(status_code=500, detail="Could not acquire lock")

        task_id = redis_instance.get(config.__TASK_KEY__['tgdd_crawl_product_link'])
        print(task_id)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            update_jobs(task_key=config.__TASK_KEY__['tgdd_crawl_product_link'], status='PENDING')
            r = crawl_product_link.delay()
            redis_instance.set(config.__TASK_KEY__['tgdd_crawl_product_link'], r.task_id)
            return _to_task_out(r, config.__TASK_KEY__['tgdd_crawl_product_link'])
        else:
            # the last task is still running!
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        lock.release()

@router.get("/description-tgdd")
def crawl_description_tgdd() -> TaskOut:
    try:
        if not lock.acquire(blocking_timeout=4):
            raise HTTPException(status_code=500, detail="Could not acquire lock")

        task_id = redis_instance.get(config.__TASK_KEY__['tgdd_crawl_description_tgdd'])
        print(task_id)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            update_jobs(task_key=config.__TASK_KEY__['tgdd_crawl_description_tgdd'], status='PENDING')
            r = crawl_description.delay()
            redis_instance.set(config.__TASK_KEY__['tgdd_crawl_description_tgdd'], r.task_id)
            return _to_task_out(r, config.__TASK_KEY__['tgdd_crawl_description_tgdd'])
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