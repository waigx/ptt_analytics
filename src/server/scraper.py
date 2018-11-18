#!/usr/bin/env python

from models import User, UserPool, Article, ArticlePool, Progress
import requests
import re
from bs4 import BeautifulSoup

ROOT_URL = "https://www.ptt.cc"
ROOT_URL = ROOT_URL.rstrip("/")
BOARD = "bbs/Gossiping"
COOKIES = {"over18": "1"}
RE_NUMBER = re.compile(r"\d+")
INDEX_MIN = 20000
ERROR_LOG = "error.log"

def url_generator(progress):
    index = requests.get("{}/{}/index.html".format(ROOT_URL, BOARD), cookies=COOKIES)
    index_html = BeautifulSoup(index.content, "html.parser")
    index_last = int(RE_NUMBER.search(index_html.find(string="‹ 上頁")
                                                .parent
                                                .get("href"))
                              .group())

    for i in range(max(progress.current_index, INDEX_MIN), index_last + 1):
        yield "/{}/index{}.html".format(BOARD, i)

request_counter = 0
request_time_total = 0

def log_error_message(error_message):
    print(error_message)
    with open(ERROR_LOG, "a") as error_log:
        error_log.write(error_message)

def retrive_html_from_url(url):
    global request_time_total, request_counter
    print("[Info]: Retriving ...")
    page = requests.get("{}{}".format(ROOT_URL, url), cookies=COOKIES) 
    if page.status_code != requests.codes.ok:
        error_message = "[Error {}]: Unable Retrive URL: {}\n".format(page.status_code, url)
        log_error_message(error_message)
        return
    round_trip = page.elapsed.total_seconds()
    request_time_total += round_trip
    request_counter += 1
    print("[Info]: Time: {}s \t Counter: {} \t Average: {}s".format(
        round_trip,
        request_counter,
        request_time_total/request_counter))
    return BeautifulSoup(page.content, "html.parser")

progress = Progress()
user_pool = UserPool()
article_pool = ArticlePool()

progress.load();
user_pool.load();
article_pool.load();

for index_url in url_generator(progress):
    print("[Info]: ".ljust(60, "="))
    print("[Index Page]: {}{}".format(ROOT_URL, index_url))
    index_html = retrive_html_from_url(index_url)

    for article_item_div in index_html.find_all(class_="title"):
        article_item_a = article_item_div.find("a") 
        if not article_item_a:
            error_message = "[Error]: On Page: {}\n" \
                            "[Error]: Unable Parse Item {}\n".format(index_url, article_item_div)
            log_error_message(error_message)
            continue
        article_url = article_item_a.get("href")
        print("[Info]: ".ljust(70, "="))
        print("[Index Page]: {}{}".format(ROOT_URL, index_url))
        print("[Article Page]: {}{}".format(ROOT_URL, article_url))
        article_html = retrive_html_from_url(article_url)

        if not article_html:
            error_message = "[Error]: On Page: {}\n" \
                            "[Error]: Unable Retrive Page {}\n".format(index_url, article_url)
            log_error_message(error_message)
            continue

        article = Article(article_html, article_url)
        article_pool.add_article(article)

        article_author = User(article_html, "article", "{}{}".format(ROOT_URL, article_url))
        user_pool.add_user(article_author)

        for comment_div in article_html.find_all(class_="push"):
            try:
                commenter = User(comment_div)
                user_pool.add_user(commenter)
            except:
                error_message = "[Error]: On Page: {}\n" \
                                "[Error]: Unable Parse Comment {}\n".format(article_url, comment_div)
                log_error_message(error_message)

    progress.current_index += 1
    progress.save()
    user_pool.save()
    article_pool.save()
