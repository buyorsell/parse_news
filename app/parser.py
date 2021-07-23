import requests
import os
import logging
from app.ner import process_news
from app.db_setup import AllNews, session
#from tqdm.notebook import tqdm
import json
from app.ml import modify_item
import datetime
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy.exc import IntegrityError

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename='parser.log', level=logging.INFO)

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

    time = soup.find("time", class_="title__cake").get("datetime")

    source = "commersant"
    response = {
        "title": header,
        "text": text,
        "rubric": list(rubric.split(",")),
        "datetime": time,
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


def dump_into_postgresql(data):
    for item_raw in data:
        item = process_news(item_raw)
        new_entry = AllNews(
            datetime=item["datetime"],
            rubric=item["rubric"],
            title=item["title"],
            text=item["text"],
            link=item["link"],
            locs=item["locs"],
            pers=item["pers"],
            orgs=item["orgs"],
        )
        processed_entry = modify_item(new_entry)
        try:
            session.add(processed_entry)
            session.commit()
        except IntegrityError:
            session.rollback()
            continue


def crawl_commersant(url_to_start):
    #    start = datetime.datetime.strptime("09-07-2021", "%d-%m-%Y")
    #    end = datetime.datetime.strptime("04-03-2011", "%d-%m-%Y")
    links = session.query(AllNews.link).all()
    opts = FirefoxOptions()
    opts.add_argument('--headless')
    driver = webdriver.Firefox(options=opts)
    actions = ActionChains(driver)
    logging.info("Starting crawler....")
    driver.get(url_to_start)
    running = True
    while running:
        try:
            while running:
                data = []
                news = driver.find_elements_by_class_name("archive_result")
                for item in news:
                    news_type = item.find_element_by_class_name(
                        "archive_result__tag").find_element_by_tag_name("a").text
                    if news_type.lower() != "лента новостей":
                        logging.info("Skipping.....")
                        continue
                    link = item.find_element_by_class_name(
                        "archive_result__item_text").find_element_by_tag_name("a").get_attribute("href")
                    logging.info(link)
                    if link not in links:
                        links.append(link)
                        try:
                            content = parse_commersant(link)
                            content["link"] = link
                            data.append(content)
                        except:
                            logging.error("Error in parser")
                            continue
                    else:
                        logging.info("Completed parsing")
                        running = False
                        return {"status": "ok"}
                if not running:
                    return {"status": "ok"}
                logging.info("Dumping into PSQL")
                dump_into_postgresql(data)
#                dump_into_json("commersant", data)
                resume = driver.find_element_by_class_name(
                    "ui_button ui_button--load_content lazyload-button")
                actions.move_to_element(resume).perform()
                resume.click()
        except NoSuchElementException:
            if not running:
                return {"status": "ok"}
            logging.info("Changing date")
            change_page = driver.find_element_by_class_name(
                "archive_date__arrow--prev")
            driver.get(change_page.get_attribute("href"))
        finally:
            if not running:
                return {"status": "ok"}
        if not running:
            return {"status": "ok"}
    logging.error("Completed")


#crawl_commersant(url_to_start)
