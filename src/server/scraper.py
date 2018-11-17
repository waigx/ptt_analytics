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
INDEX_MIN = 999

def url_generator(progress):
    index = requests.get("{}/{}/index.html".format(ROOT_URL, BOARD), cookies=COOKIES)
    index_html = BeautifulSoup(index.content, "html.parser")
    index_last = int(RE_NUMBER.search(index_html.find(string="‹ 上頁")
                                                .parent
                                                .get("href"))
                              .group())

    for i in range(max(progress.current_index, INDEX_MIN), index_last + 1):
        yield "/{}/index{}.html".format(BOARD, i)


progress = Progress()
user_pool = UserPool()
article_pool = ArticlePool()

progress.load();
user_pool.load();
article_pool.load();

for index_url in url_generator(progress):
    print("[Info]: ".ljust(60, "="))
    print("[Index Page]: {}{}".format(ROOT_URL, index_url))
    index_page = requests.get("{}{}".format(ROOT_URL, index_url), cookies=COOKIES) 
    index_html = BeautifulSoup(index_page.content, "html.parser")

    for article_url in [div.find('a').get('href') for div in index_html.find_all(class_="title")]:
        print("[Info]: ".ljust(60, "="))
        print("[Index Page]: {}{}".format(ROOT_URL, index_url))
        print("[Article Page]: {}{}".format(ROOT_URL, article_url))
        article_page = requests.get("{}{}".format(ROOT_URL, article_url), cookies=COOKIES)
        article_html = BeautifulSoup(article_page.content, "html.parser")

        article = Article(article_html, article_url)
        article_pool.add_article(article)

        article_author = User(article_html, "article", "{}{}".format(ROOT_URL, article_url))
        user_pool.add_user(article_author)

        for comment_div in article_html.find_all(class_="push"):
            commenter = User(comment_div)
            user_pool.add_user(commenter)

    progress.current_index += 1
    progress.save()
    user_pool.save()
    article_pool.save()
