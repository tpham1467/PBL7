# lib
import config
import task
from celery.result import AsyncResult
from database.mysql_connector import update_jobs, update_jobs_by_task_id

# entities
from entities import TaskOut
from fastapi import APIRouter, HTTPException
from redis import Redis
from redis.lock import Lock as RedisLock
from task import (
    crawl_category_task,
    crawl_description,
    crawl_end_page_link_category,
    crawl_product_link,
    test_sleep,
)

router = APIRouter(prefix="/crawl")

try:
    redis_instance = Redis.from_url(task.redis_url)
    redis_instance.ping()  # Check if the Redis server is reachable
    print("Connected to Redis")
except ConnectionError as e:
    print(f"Failed to connect to Redis: {e}")
    raise RuntimeError(f"Failed to connect to Redis: {e}")

lock = RedisLock(redis_instance, name="task_id")


@router.get("/category-tgdd")
def crawl_category_tgdd() -> TaskOut:
    execute_task("tgdd_crawl_category", crawl_category_task)

        task_id = redis_instance.get(config.__TASK_KEY__["tgdd_crawl_category"])
        print(task_id)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            update_jobs(
                task_key=config.__TASK_KEY__["tgdd_crawl_category"], status="PENDING"
            )
            r = crawl_category_task.delay()
            redis_instance.set(config.__TASK_KEY__["tgdd_crawl_category"], r.task_id)
            return _to_task_out(r, config.__TASK_KEY__["tgdd_crawl_category"])
        else:
            # the last task is still running!
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        lock.release()


@router.get("/end-page-link-tgdd")
def crawl_end_page_tgdd() -> TaskOut:
    execute_task("tgdd_crawl_end_page_link", crawl_end_page_link_category)

        task_id = redis_instance.get(config.__TASK_KEY__["tgdd_crawl_end_page_link"])
        print(task_id)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            update_jobs(
                task_key=config.__TASK_KEY__["tgdd_crawl_end_page_link"],
                status="PENDING",
            )
            r = crawl_end_page_link_category.delay()
            redis_instance.set(
                config.__TASK_KEY__["tgdd_crawl_end_page_link"], r.task_id
            )
            return _to_task_out(r, config.__TASK_KEY__["tgdd_crawl_end_page_link"])
        else:
            # the last task is still running!
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        lock.release()


@router.get("/product-link-tgdd")
def crawl_product_tgdd() -> TaskOut:
    execute_task("tgdd_crawl_product_link", crawl_product_link)

        task_id = redis_instance.get(config.__TASK_KEY__["tgdd_crawl_product_link"])
        print(task_id)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            update_jobs(
                task_key=config.__TASK_KEY__["tgdd_crawl_product_link"],
                status="PENDING",
            )
            r = crawl_product_link.delay()
            redis_instance.set(
                config.__TASK_KEY__["tgdd_crawl_product_link"], r.task_id
            )
            return _to_task_out(r, config.__TASK_KEY__["tgdd_crawl_product_link"])
        else:
            # the last task is still running!
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        lock.release()


@router.get("/description-tgdd")
def crawl_description_tgdd() -> TaskOut:
    execute_task("tgdd_crawl_description_tgdd", crawl_description)

        task_id = redis_instance.get(config.__TASK_KEY__["tgdd_crawl_description_tgdd"])
        print(task_id)
        if task_id is None or task.app.AsyncResult(task_id).ready():
            # no task was ever run, or the last task finished already
            update_jobs(
                task_key=config.__TASK_KEY__["tgdd_crawl_description_tgdd"],
                status="PENDING",
            )
            r = crawl_description.delay()
            redis_instance.set(
                config.__TASK_KEY__["tgdd_crawl_description_tgdd"], r.task_id
            )
            return _to_task_out(r, config.__TASK_KEY__["tgdd_crawl_description_tgdd"])
        else:
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        if lock_acquired:
            lock.release()



def _to_task_out(r: AsyncResult, type: str) -> TaskOut:
    print("Update Task into DB...")
    update_jobs_by_task_id(type, task_id=r.task_id)
    return TaskOut(id=r.task_id, status=r.status)
