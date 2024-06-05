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
    update_jobs(config.__TASK_KEY__['preprocess'], 'IN_PROGRESS')
    try:
        thegioididong.driver
        base_link = "https://www.thegioididong.com/"
        removing_keyword = ['op-lung', 'mieng-dan', 'ldp', 'tien-ich/', 'gia-do-dien-thoai', 'tui-dung-airpods', 'tui-chong-soc', 'sim-so-dep']
        categories = ['dtdd', 'laptop-ldp', 'may-tinh-bang']
        categories = thegioididong.crawl_category(base_link, categories,removing_keyword)
        print(categories)
        dir = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_categories'] + '.csv'
        thegioididong.write_to_csv(categories, dir, ["category", "full link"], False)
    except:
        update_jobs(config.__TASK_KEY__['preprocess'], 'FAILED')

    update_jobs(config.__TASK_KEY__['preprocess'], 'SUCCESS')
    print('-----End crawl-----')
    return categories
    
@app.task
def preprocess_data():
    print('-----Begin preprocess-----')
    data_path = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_description'] + '.csv'
    preprocess_path = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_description_preprocessed'] + '.csv'
    preprocess.preprocess_data(data_path = data_path, preprocess_path = preprocess_path)
    print('-----End preprocess-----')

@app.task
def crawl_end_page_link_category():
    print('-----Begin crawl-----')
    update_jobs(config.__TASK_KEY__['tgdd_crawl_end_page_link'], 'IN_PROGRESS')
    try:
        thegioididong.driver
        end_page_link = []
        category_dir = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_categories'] + '.csv'
        end_page_link_dir = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_end_page_link'] + '.csv'
        for i in  thegioididong.read_csv(category_dir, True):
            end_page_link.append([i[0], thegioididong.get_end_page_from_category(i[1])])
            # thegioididong.driver.close()

        thegioididong.write_to_csv(end_page_link, end_page_link_dir, ["category", "full link"], False)
    except:
        update_jobs(config.__TASK_KEY__['tgdd_crawl_end_page_link'], 'FAILED')

    update_jobs(config.__TASK_KEY__['tgdd_crawl_end_page_link'], 'SUCCESS')
    # thegioididong.driver.quit()
    print('-----End crawl-----')
    return end_page_link


@app.task
def crawl_product_link():
    print('-----Begin crawl-----')
    update_jobs(config.__TASK_KEY__['tgdd_crawl_product_link'], 'IN_PROGRESS')
    try:
        base_link = "https://www.thegioididong.com/"
        end_page_link_dir = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_end_page_link'] + '.csv'
        product_link_dir = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_product_link'] + '.csv'
        result = []
        for i in thegioididong.read_csv(end_page_link_dir, True):
            data = thegioididong.crawl_list(base_link, i[1])
            result.append(data)
            thegioididong.write_to_csv(data, product_link_dir, ["name", "category", "Link"], False, True)
    except:
        update_jobs(config.__TASK_KEY__['tgdd_crawl_end_page_link'], 'FAILED')
    update_jobs(config.__TASK_KEY__['tgdd_crawl_end_page_link'], 'SUCCESS')
    # thegioididong.driver.quit()
    print('-----End crawl-----')
    return result

@app.task
def crawl_description():
    print('-----Begin crawl-----')
    update_jobs(config.__TASK_KEY__['tgdd_crawl_description_tgdd'], 'IN_PROGRESS')
    try:
        thegioididong.driver
        product_link_dir = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_product_link'] + '.csv'
        product_description_dir = file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_description'] + '.csv'
        result = []
        for i in thegioididong.read_csv(product_link_dir, True):
            data = thegioididong.crawl_description(i[1], i[2], [])
            result.append(data)
            thegioididong.write_to_csv(data, product_description_dir, ["name", "description"], False, True)
    except:
        update_jobs(config.__TASK_KEY__['tgdd_crawl_description_tgdd'], 'FAILED')
    update_jobs(config.__TASK_KEY__['tgdd_crawl_description_tgdd'], 'SUCCESS')
    print('-----End crawl-----')
    return result



@app.task
def test_sleep():
    update_jobs(config.__TASK_KEY__['tgdd_crawl_description_tgdd'], 'IN_PROGRESS')

    thegioididong.test()

    update_jobs(config.__TASK_KEY__['tgdd_crawl_description_tgdd'], 'SUCCESS')
    print('-----End crawl-----')