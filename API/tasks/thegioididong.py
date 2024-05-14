from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlparse
from selenium.webdriver.chrome.service import Service

import csv
import re
import time
import os
import csv
import pandas as pd

service = Service()
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


driver = webdriver.Chrome(service=service, options=options)


def remove_last_slash(link):
    if link.endswith("/"):
        remove_link = link[:-1]
        return remove_link
    return link

def remove_first_slash(link):
    if link.startswith("/"):
        remove_link = link[1:]
        return remove_link
    return link

def crawl_category(base_link, categories, remove_key_word):
    driver.get(base_link)
    content = driver.page_source
    result = []
    soup = BeautifulSoup(content, "html.parser")
    menu = soup.find('ul', class_='main-menu')
    list_a =  menu.findChildren('a')
    base_link_remove_last_slash = remove_last_slash(base_link)
    for i in list_a:
        if not any (word in i.get('href') for word in remove_key_word) and i.get('href') != None and check_keywords_in_link(i.get('href'), categories):
            cate_link = base_link_remove_last_slash + i.get('href')
            result.append([remove_first_slash(i.get('href')), cate_link])
            print([remove_first_slash(i.get('href')), cate_link])
    return result

def check_keywords_in_link(link, keywords):
    keyword_pattern = re.compile('|'.join(keywords), re.IGNORECASE)
    return bool(keyword_pattern.search(link))

def write_to_csv(data, path, column_names, index = True, append=False):
    if data == None: 
        return "Data is null"
    if index == True:
        #Đánh index cho mỗi record
        data = [(i+1, item) for i, item in enumerate(data)]
    # check xem có phải là chế độ ghi liên tiếp hay không
    if append:
        # Tồn tại file đó hay không
        if not os.path.exists(path):
            # Nếu tập tin chưa tồn tại, tạo DataFrame từ dữ liệu và ghi vào tập tin
            df = pd.DataFrame(data, columns=column_names)
            df.to_csv(path, index=False)
            return "Data has written to csv file"
        df = pd.DataFrame(data)
        df.to_csv(path, mode='a', header=False, index=False)
        
    else:   
        if not os.path.exists(path):
            # Nếu tập tin chưa tồn tại, tạo DataFrame từ dữ liệu và ghi vào tập tin
            df = pd.DataFrame(data, columns=column_names)
            df.to_csv(path, index=False)
            return "Data has written to csv file"
        else:
            os.remove(path)
            print ("Found a csv file, deleting it...")
            df = pd.DataFrame(data, columns=column_names)
            df.to_csv(path, index=False)
            return "Data has written to csv file"