import requests
import os
import logging
import json
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import datetime
from db_setup import session, Meduza
from sqlalchemy.exc import IntegrityError
from ner_handler import process_news



for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename='meduza_parser.log', level=logging.INFO)


url_to_start = "https://meduza.io/"


def replace_month(x):
    return x.replace("января", "01").replace("февраля", "02").replace("марта", "03").replace("апреля", "04").replace("мая", "05").replace("июня", "06").replace("июля", "07").replace("августа", "08").replace("сентября", "09").replace("октября", "10").replace("ноября", "11").replace("декабря", "12")


def parse_meduza(url_to_parse):
    html_page = requests.get(url_to_parse)

    soup = BeautifulSoup(html_page.content, 'html.parser')

    page_header = soup.find('div', class_='GeneralMaterial-materialHeader')

    news_header = page_header.find('h1')
    news_time = soup.find('time')
    time = str(datetime.strptime(replace_month(
        news_time.text), '%H:%M, %d %m %Y'))
    try:
        news_source = page_header.find('div').find('a')
        source = news_source.text
    except:
        source = "meduza"
    news_content = soup.find('div', class_='GeneralMaterial-article')
    news_text = news_content.find_all('p')
    text = ""
    for paragraph in news_text:
        text += paragraph.text + "\n"
    response = {
        "title": news_header.text,
        "text": text.replace('\xa0', " "),
        "datetime": time,
        "tags": [],
        "source": source,
        "author": "",
    }
    return response


def dump_into_postgresql(data):
    for item_raw in data:
        item = process_news(item_raw)
        new_entry = Meduza(
            datetime=item["datetime"],
            title=item["title"],
            source=item["source"],
            text=item["text"],
            link=item["link"],
            locs=item["locs"],
            pers=item["pers"],
            orgs=item["orgs"],
        )
        try:
            session.add(new_entry)
            session.commit()
        except IntegrityError:
            session.rollback()
            continue


def crawl_meduza(url_to_start):
    links = []
    opts = FirefoxOptions()
    opts.add_argument('--headless')
    driver = webdriver.Firefox(options=opts)
    actions = ActionChains(driver)
    logging.info("start parsing")
    driver.get(url_to_start)
    gdpr_panel_dismiss = driver.find_element_by_class_name("GDPRPanel-dismiss")
    gdpr_panel_dismiss.click()
    switch = driver.find_element_by_tag_name("input")
    switch.click()
    while True:
        data = []
        news = driver.find_elements_by_class_name("ChronologyItem-link")
        for item in news[-24:]:
            link = item.get_attribute('href')
            logging.info(link)
            if link not in links:
                links.append(link)
                if "/feature/" in link or "/news/" in link:
                    content = parse_meduza(link)
                    content["link"] = link
                    data.append(content)
                else:
                    logging.warning("skipping link")
                    continue
            else:
                logging.warning("link already parsed")
        if len(data) != 0:
            dump_into_postgresql(data)
            #dump_into_json("meduza", data)
        resume = driver.find_element_by_css_selector(
            "button[class^='Button-module_root']")
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        footer = driver.find_element_by_class_name("Footer-giphy")
        actions.move_to_element(footer).perform()
        resume.click()
    logging.error("parser crashed")


def dump_into_json(site, data):
    counter = 0
    while os.path.isfile(site + "-" + str(counter) + ".json"):
        counter += 1
    with open(site + "-" + str(counter) + ".json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False)


crawl_meduza(url_to_start)
