# lib
import config
import task
from celery import chain, group
from celery.result import AsyncResult
from database.mysql_connector import (
    get_task_status,
    get_tasks_status,
    update_jobs,
    update_jobs_by_task_id,
)

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

print(lock)


@router.get("/category-tgdd")
def crawl_category_tgdd() -> TaskOut:
    return execute_task("tgdd_crawl_category", crawl_category_task)


@router.get("/end-page-link-tgdd")
def crawl_end_page_tgdd() -> TaskOut:
    return execute_task("tgdd_crawl_end_page_link", crawl_end_page_link_category)


@router.get("/product-link-tgdd")
def crawl_product_tgdd() -> TaskOut:
    return execute_task("tgdd_crawl_product_link", crawl_product_link)


@router.get("/description-tgdd")
def crawl_description_tgdd() -> TaskOut:
    return execute_task("tgdd_crawl_description_tgdd", crawl_description)


@router.get("/start-all-tasks")
def start_all_tasks() -> list[TaskOut]:
    # Check if there is any task in progress
    if any(task["status"] == "IN_PROGRESS" for task in get_tasks_status()):
        raise HTTPException(status_code=400, detail="Another task is in progress")

    # Initialize an empty list to hold the results of each task
    task_results = []

    # Execute each task and append the result to the list
    task_results.append(execute_task("tgdd_crawl_category", crawl_category_task))
    task_results.append(
        execute_task("tgdd_crawl_end_page_link", crawl_end_page_link_category)
    )
    task_results.append(execute_task("tgdd_crawl_product_link", crawl_product_link))
    task_results.append(execute_task("tgdd_crawl_description_tgdd", crawl_description))

    # Return the list of task results
    return task_results


def execute_task(task_key, task_function) -> TaskOut:
    print(f"{task_key}, {task_function}")
    try:
        if not lock.acquire(blocking_timeout=4):
            raise HTTPException(status_code=500, detail="Could not acquire lock")

        task_id = redis_instance.get(config.__TASK_KEY__[task_key])
        print(f"task_id1: {task_id}")

        if task_id is None or task.app.AsyncResult(task_id).ready():
            print(f"task_id2: {task_id}")
            update_jobs(task_key=config.__TASK_KEY__[task_key], status="PENDING")
            print("update jobs completed")
            r = task_function.delay()
            print(f"result:{r}")
            redis_instance.set(config.__TASK_KEY__[task_key], r.task_id)
            return _to_task_out(r, config.__TASK_KEY__[task_key])
        else:
            raise HTTPException(
                status_code=400, detail="A task is already being executed"
            )
    finally:
        lock.release()


def _to_task_out(r: AsyncResult, type: str) -> TaskOut:
    print("Update Task into DB...")
    update_jobs_by_task_id(type, task_id=r.task_id)
    return TaskOut(id=r.task_id, status=r.status)
