#!/usr/bin/env python

from models import User, UserPool, Article, ArticlePool, Progress
import requests
import re
from bs4 import BeautifulSoup

#page = requests.get("https://www.ptt.cc/bbs/Gossiping/index20373.html", cookies={"over18":"1"})
#bs = BeautifulSoup(page.content, "html.parser")
#print(list(div.find("a") for div in list(bs.find_all(class_="title"))))

#ap = ArticlePool()
#ap.load()
prg = Progress()
prg.load()
#print(len(ap.articles))
print(prg.current_index)
