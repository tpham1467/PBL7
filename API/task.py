import time
from celery import Celery
import os
from datetime import datetime
from database.mysql_connector import update_jobs
from services import file_management
from tasks import thegioididong, preprocess
import config

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

app = Celery(__name__, broker=redis_url, backend=redis_url)

@app.task
def dummy_task():
    time.sleep(20)
    folder = "/tmp/celery"
    os.makedirs(folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%s")
    with open(f"{folder}/task-{now}.txt", "w") as f:
        f.write("hello!")

@app.task
def crawl_category_task():
    print('-----Begin crawl-----')
    thegioididong.driver
    base_link = "https://www.thegioididong.com/"
    removing_keyword = ['op-lung', 'mieng-dan', 'ldp', 'tien-ich/', 'gia-do-dien-thoai', 'tui-dung-airpods', 'tui-chong-soc', 'sim-so-dep']
    categories = ['dtdd', 'laptop-ldp', 'may-tinh-bang']
    categories = thegioididong.crawl_category(base_link, categories,removing_keyword)
    print(categories)
    dir = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_categories'] + '.csv'
    thegioididong.write_to_csv(categories, dir, ["category", "full link"], False)
    thegioididong.driver.quit()
    # update_jobs('SUCCESS', config.__TASK_KEY__['preprocess'])
    print('-----End crawl-----')
    return categories
    
@app.task
def preprocess_data():
    print('-----Begin preprocess-----')
    data_path = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_description'] + '.csv'
    preprocess_path = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_description_preprocessed'] + '.csv'
    preprocess.preprocess_data(data_path = data_path, preprocess_path = preprocess_path)
    update_jobs(status='SUCCESS',task_key=config.__TASK_KEY__['preprocess'])
    print('-----End preprocess-----')
    