#!/usr/bin/env python

from models import User, UserPool
import requests
from bs4 import BeautifulSoup

ROOT = "https://www.ptt.cc/"
ROOT = ROOT.rstrip("/")
COOKIES = {"over18": "1"}

up = UserPool()
up.load()

page = requests.get(ROOT + "/bbs/Gossiping/index39445.html", cookies=COOKIES)
soup = BeautifulSoup(page.content, 'html.parser')

for item in soup.find_all(class_="title"):
    link = item.find('a').get('href')
    addr = ROOT + link
    article = requests.get(addr, cookies=COOKIES)
    article_html = BeautifulSoup(article.content, 'html.parser')
    author = User(article_html, "article", link)
    up.add_user(author)
    print(link, author.id)

    for comment_html in article_html.find_all(class_="push"):
       commenter = User(comment_html)
       up.add_user(commenter)

up.save()
