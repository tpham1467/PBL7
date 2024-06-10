# lib
import config
import task
from celery.result import AsyncResult
from database.mysql_connector import get_all_jobs
from entities import TaskOut
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from redis import Redis
from redis.lock import Lock as RedisLock
import requests
# entities
redis_instance = Redis.from_url(task.redis_url)
router = APIRouter(prefix="/model")


class TextRequest(BaseModel):
    text: str

@router.get("/predict")
def tracking(request: TextRequest):

    text = request.text

    print(text)

    url = 'http://recommender_system:7010/predict'
    
    incorrect_payload = {
    'text': text
    }
    
    response = requests.post(url, json=incorrect_payload)
    
    data1 = response.json()

    return data1
