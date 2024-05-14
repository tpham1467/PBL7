from celery import Celery
import os
from datetime import datetime
from tasks import thegioididong

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

app = Celery(__name__, broker=redis_url, backend=redis_url)

@app.task
def dummy_task():
    folder = "/tmp/celery"
    os.makedirs(folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%s")
    with open(f"{folder}/task-{now}.txt", "w") as f:
        f.write("hello!")

@app.task
def crawl_category():
    print('-----Begin crawl-----')
    thegioididong.driver
    base_link = "https://www.thegioididong.com/"
    removing_keyword = ['op-lung', 'mieng-dan', 'ldp', 'tien-ich/', 'gia-do-dien-thoai', 'tui-dung-airpods', 'tui-chong-soc', 'sim-so-dep']
    categories = ['dtdd', 'laptop-ldp', 'may-tinh-bang']
    categories = thegioididong.crawl_category(base_link, categories,removing_keyword)
    print(categories)
    thegioididong.write_to_csv(categories, "./data/tgdt_categories.csv",["category", "full link"], False)
    thegioididong.driver.quit()