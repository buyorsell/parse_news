import requests
import os
from tqdm.notebook import tqdm
import json
import datetime
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

url_to_start = "https://www.kommersant.ru/archive/rubric/3/day/2019-08-05"


def parse_commersant(url_to_parse):
    html_page = requests.get(url_to_parse)
    soup = BeautifulSoup(html_page.content, 'html.parser')

    news_body = soup.find("div", class_="lenta js-lenta").find("article")

    author = news_body.get("data-article-authors")

    header = news_body.find("header").find(
        "div", class_="text").find("h1").text

    try:
        subheader = news_body.find("header").find("div", class_="text").find(
            "h1", class_="article_subheader").text
    except:
        subheader = ""

    rubric = news_body.get("data-article-categories")

    body = news_body.find(
        "div", class_="article_text_wrapper").find_all("p", class_="b-article__text")

    text = ""
    for item in body:
        text += item.text + "\n"

    datetime = soup.find("time", class_="title__cake").get("datetime")

    source = "commersant"
    response = {
        "header": header,
        "text": text,
        "rubric": rubric,
        "datetime": datetime,
        "subheader": subheader,
        "tags": [],
        "source": source,
    }
    return response


def dump_into_json(site, data):
    counter = 0
    while os.path.isfile(site + "-" + str(counter) + ".json"):
        counter += 1
    with open(site + "-" + str(counter) + ".json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False)


def crawl_commersant(url_to_start):
    start = datetime.datetime.strptime("05-08-2019", "%d-%m-%Y")
    end = datetime.datetime.strptime("04-03-2011", "%d-%m-%Y")
    links = []
    opts = FirefoxOptions()
    opts.add_argument('--headless')
    driver = webdriver.Firefox(options=opts)
    actions = ActionChains(driver)
    print("check")
    driver.get(url_to_start)
    for item in tqdm(range(0, (start-end).days)):
        print("start")
        try:
            while True:
                data = []
                news = driver.find_elements_by_class_name("archive_result")
                for item in news:
                    news_type = item.find_element_by_class_name(
                        "archive_result__tag").find_element_by_tag_name("a").text
                    if news_type.lower() != "лента новостей":
                        print("skipping")
                        continue
                    link = item.find_element_by_class_name(
                        "archive_result__item_text").find_element_by_tag_name("a").get_attribute("href")
                    print(link)
                    if link not in links:
                        links.append(link)
                        content = parse_commersant(link)
                        data.append(content)
                dump_into_json("commersant", data)
                resume = driver.find_element_by_class_name(
                    "ui_button ui_button--load_content lazyload-button")
                actions.move_to_element(resume).perform()
                resume.click()
        except NoSuchElementException:
            change_page = driver.find_element_by_class_name(
                "archive_date__arrow--prev")
            driver.get(change_page.get_attribute("href"))


crawl_commersant(url_to_start)
