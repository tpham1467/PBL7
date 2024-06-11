import csv
import os
import re
import time
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

service = Service()
options = webdriver.ChromeOptions()
options.add_argument("enable-automation")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-browser-side-navigation")
options.add_argument("--disable-extensions")
# Blocking Images and Resources in Selenium
prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.default_content_setting_values.javascript": 2,
}

options.add_experimental_option("prefs", prefs)


driver = webdriver.Chrome(service=service, options=options)


def split_url(url):
    # Sử dụng biểu thức chính quy để tìm vị trí của kí tự số cuối cùng
    match = re.search(r"\d+$", url)
    if match:
        # Nếu tìm thấy, lấy vị trí của kí tự số cuối cùng
        poi = match.start()
        # Tách chuỗi thành hai phần
        prefix = url[:poi]
        endfix = url[poi:]
        return prefix, endfix
    else:
        # Nếu không tìm thấy kí tự số cuối cùng, trả về None cho cả hai phần
        return url, ""


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
    menu = soup.find("ul", class_="main-menu")
    list_a = menu.findChildren("a")
    base_link_remove_last_slash = remove_last_slash(base_link)
    for i in list_a:
        if (
            not any(word in i.get("href") for word in remove_key_word)
            and i.get("href") != None
            and check_keywords_in_link(i.get("href"), categories)
        ):
            cate_link = base_link_remove_last_slash + i.get("href")
            result.append([remove_first_slash(i.get("href")), cate_link])
            print([remove_first_slash(i.get("href")), cate_link])
    return result


def check_keywords_in_link(link, keywords):
    keyword_pattern = re.compile("|".join(keywords), re.IGNORECASE)
    return bool(keyword_pattern.search(link))


def write_to_csv(data, path, column_names, index=True, append=False):
    if data == None:
        return "Data is null"
    if index == True:
        # Đánh index cho mỗi record
        data = [(i + 1, item) for i, item in enumerate(data)]
    # check xem có phải là chế độ ghi liên tiếp hay không
    if append:
        # Tồn tại file đó hay không
        if not os.path.exists(path):
            # Nếu tập tin chưa tồn tại, tạo DataFrame từ dữ liệu và ghi vào tập tin
            df = pd.DataFrame(data, columns=column_names)
            df.to_csv(path, index=False)
            return "Data has written to csv file"
        df = pd.DataFrame(data)
        df.to_csv(path, mode="a", header=False, index=False)

    else:
        if not os.path.exists(path):
            # Nếu tập tin chưa tồn tại, tạo DataFrame từ dữ liệu và ghi vào tập tin
            df = pd.DataFrame(data, columns=column_names)
            df.to_csv(path, index=False)
            return "Data has written to csv file"
        else:
            os.remove(path)
            print("Found a csv file, deleting it...")
            df = pd.DataFrame(data, columns=column_names)
            df.to_csv(path, index=False)
            return "Data has written to csv file"


def crawl_description(product_name, product_link, remove_key_word):
    print("crawl_description")
    result = []
    suffix = "#top-article"
    current_link = product_link + suffix
    driver.get(current_link)
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")
    content_article = soup.find("div", class_="content-article")
    if content_article != None:
        p_tags = content_article.find_all("p")
        for p in p_tags:
            if p.text != "":
                result.append([product_name, p.text])
                print(p.text)
    return result


def read_csv(path, is_read_header=True):
    data = []
    if not os.path.exists(path):
        print(f"File '{path}' does not exist.")
        return data
    # Mở tập tin CSV để đọc
    with open(path, "r", newline="") as file:
        reader = csv.reader(file)
        if is_read_header:
            next(reader)
        # Duyệt qua từng hàng trong tập tin CSV
        for row in reader:
            data.append(row)
    return data


def get_end_page_from_category(url):
    print("Current session is {}".format(driver.session_id))
    # first find url
    driver.get(url)
    category_url = ""
    try:
        driver.find_element(By.CLASS_NAME, "view-more")
        driver.find_element(By.CLASS_NAME, "view-more > a").click()
        time.sleep(5)
        category_url = driver.current_url
    except:
        category_url = url

    pre, end = split_url(category_url)
    print(pre, end)
    if pre != "" and end != "":
        stop = False
        end_url = pre
        count = int(end)
        while stop == False:
            driver.get(end_url + str(count))
            try:
                driver.find_element(By.CLASS_NAME, "view-more")
                driver.find_element(By.CLASS_NAME, "view-more > a").click()
                time.sleep(5)
                count += 1
                end_url = driver.current_url
            except:
                stop = True

        end = count
        print(pre + str(end))

    return pre + str(end)


def crawl_list(base_link, url):
    driver.get(url)
    content = driver.page_source
    remove_key_words = ["javascript:void(0)", "#"]
    list_href = []
    soup = BeautifulSoup(content, "html.parser")

    list_products = soup.find("ul", class_="listproduct")
    base_link_remove_last_slash = remove_last_slash(base_link)
    if list_products != None:
        li_products = list_products.findChildren("li")
        for li in li_products:
            a_products = li.findChildren("a")
            for a in a_products:
                if not any(word in a.get("href") for word in remove_key_words):
                    product_url = base_link_remove_last_slash + a.get("href")
                    list_href.append([a.get("data-name"), a.get("href"), product_url])

        print(f"Get {len(li_products)} from {url}")

    return list_href
