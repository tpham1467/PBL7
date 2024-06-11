# lib
import re
from typing import Counter

import config
import pandas as pd
import task
from celery import chain, group
from celery.result import AsyncResult
from database.mysql_connector import (
    is_any_task_in_progress,
    update_jobs,
    update_jobs_by_task_id,
)

# entities
from entities import TaskOut
from fastapi import APIRouter, HTTPException
from redis import Redis
from redis.lock import Lock as RedisLock
from services import file_management
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


@router.get("/tgdd_crawl_category")
def crawl_category_tgdd() -> TaskOut:
    return execute_task(config.__TASK_KEY__["tgdd_crawl_category"], crawl_category_task)


@router.get("/tgdd_crawl_end_page_link")
def crawl_end_page_tgdd() -> TaskOut:
    return execute_task(
        config.__TASK_KEY__["tgdd_crawl_end_page_link"], crawl_end_page_link_category
    )


@router.get("/tgdd_crawl_product_link")
def crawl_product_tgdd() -> TaskOut:
    return execute_task(
        config.__TASK_KEY__["tgdd_crawl_product_link"], crawl_product_link
    )


@router.get("/tgdd_crawl_description")
def crawl_description_tgdd() -> TaskOut:
    return execute_task(
        config.__TASK_KEY__["tgdd_crawl_description"], crawl_description
    )


@router.get("/start-all-tasks")
def start_all_tasks() -> list[TaskOut]:
    # Check if there is any task in progress
    if is_any_task_in_progress():
        raise HTTPException(status_code=400, detail="Another task is in progress")

    # Initialize an empty list to hold the results of each task
    task_results = []

    # Execute each task and append the result to the list
    task_results.append(execute_task("tgdd_crawl_category", crawl_category_task))
    task_results.append(
        execute_task("tgdd_crawl_end_page_link", crawl_end_page_link_category)
    )
    task_results.append(execute_task("tgdd_crawl_product_link", crawl_product_link))
    task_results.append(execute_task("tgdd_crawl_description", crawl_description))

    # Return the list of task results
    return task_results


def execute_task(task_key, task_function) -> TaskOut:
    print(f"{task_key}, {task_function}")
    try:
        if not lock.acquire(blocking_timeout=4):
            raise HTTPException(status_code=500, detail="Could not acquire lock")

        task_id = redis_instance.get(config.__TASK_KEY__[task_key])
        # print(f"task_id1: {task_id}")

        if task_id is None or task.app.AsyncResult(task_id).ready():
            # print(f"task_id2: {task_id}")
            update_jobs(task_key=config.__TASK_KEY__[task_key], status="PENDING")
            # print("update jobs completed")
            r = task_function.delay()
            # print(f"result:{r}")
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


@router.get("/crawl-result")
def get_crawl_result():
    data_path = (
        file_management.__path__["crawl_data"]
        + "/"
        + file_management.__file_name__["tgdd_crawl_description"]
        + ".csv"
    )

    return analyze_csv(data_path)


def get_categories_from_csv(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Extract the 'category' column and convert it to a list
    categories = df["category"].tolist()
    print(f"categories: {categories}")

    return categories


def analyze_csv(file_path):

    category_csv_path = (
        file_management.__path__["crawl_data"]
        + "/"
        + file_management.__file_name__["tgdd_crawl_category"]
        + ".csv"
    )
    categories = get_categories_from_csv(category_csv_path)

    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Initialize a dictionary to store the word and sentence counts for each category
    category_stats = {
        category: {"words_count": 0, "sentence_count": 0} for category in categories
    }

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Extract the name and description from the row
        name = row["name"]
        description = row["description"]

        # Split the description into words and sentences
        words = description.split()
        sentences = description.split("•")

        # Determine the category based on the name
        for category in categories:
            if f"/{category}/" in name:
                # Update the word and sentence counts for the category
                category_stats[category]["words_count"] += len(words)
                category_stats[category]["sentence_count"] += (
                    len(sentences) - 1
                )  # Subtract 1 because the first element is an empty string
                break

    return category_stats
