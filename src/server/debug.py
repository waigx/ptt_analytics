#!/usr/bin/env python

from models import User, UserPool, Article, ArticlePool, Progress
import requests
import re
from bs4 import BeautifulSoup

#page = requests.get("https://www.ptt.cc/bbs/Gossiping/M.1513517665.A.7BA.html", cookies={"over18":"1"})
#bs = BeautifulSoup(page.content, "html.parser")
#print(list(bs.find(class_="article-meta-value").strings))

ap = ArticlePool()
ap.load()
prg = Progress()
prg.load()
print([id.nag_users for id in ap.articles.values()])
print(prg.current_index)
