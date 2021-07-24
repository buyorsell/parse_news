import requests
import os, sys
import logging
from app.ner import process_news
from app.db_setup import AllNews, session
from app.wordcloud import makecloud
#from tqdm.notebook import tqdm
import json
from app.ml import modify_item
import datetime
from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)

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
        makecloud(processed_entry)
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
    logging.warning("Starting crawler....")
    html_page = requests.get(url_to_start)
    running = True
    while running:
        soup = BeautifulSoup(html_page.content, 'html.parser')
        data = []
        news = soup.find_all("article", class_="archive_result")
        if len(news) == 0:
            return {"status": "ok"}
        for item in news:
            news_type = item.find( "p", class_="archive_result__tag").find("a").text
            if "лентановостей" not in news_type.lower().replace("\n", "").replace(" ", ""):
                logging.info("Skipping.....")
                continue
            link = "https://www.kommersant.ru" + \
                item.find("div", class_="archive_result__item_text").find(
                    "a").get("href")
            logging.warning(link)
            if link not in links:
                links.append(link)
                content = parse_commersant(link)
                content["link"] = link
                data.append(content)
            else:
                logging.warning("Completed parsing")
                running = False
                return {"status": "ok"}
        if not running:
            return {"status": "ok"}
        logging.warning("Dumping into PSQL")
        dump_into_postgresql(data)
    logging.warning("Changing date")
    change_page = soup.find("a", "archive_date__arrow--prev")
    html_page = requests.get(change_page.get("href"))
    logging.error("Completed")


#crawl_commersant(url_to_start)
