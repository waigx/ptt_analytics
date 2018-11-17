#!/usr/bin/env python

import pickle
import os
import re
from collections import defaultdict

RE_IP = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
RE_ARTICLE = re.compile(r"[\s\S]{80,}")

def get_path(file_path):
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.path.dirname(__file__), file_path)
    return file_path

class User:
    def __init__(self, content, content_type="comment", url=None):
        id, ip = self.parse_user(content, content_type, url)
        self.id = id
        self.ips = {ip}
        print("[User]: ID: {:<32} from IP: {}".format(id, ip or "Unknown"))

    def parse_user(self, content, content_type, url):
        def get_ip_from_text(text):
            match_obj = RE_IP.search(text.string)
            return match_obj.group() if match_obj else ""

        if content_type == "comment":
            id = content.find(class_="push-userid").string.split()[0]
            ip_container = content.find(class_="push-ipdatetime").string
            ip = get_ip_from_text(ip_container.string)
        elif content_type == "article":
            id = next(content.find(class_="article-meta-value").strings).split()[0]
            url_container = content.find(string=url)
            if url_container:
                ip = get_ip_from_text(url_container.parent.parent.previous_sibling.string)
            else:
                ip = ""
        return str(id), str(ip)

class UserPool:
    DEFAULT_FILE_NAME = "user_pool.pk"

    def __init__(self):
        self.users = {}
        self.ips = defaultdict(set)

    def load(self, file_path=None):
        file_path = get_path(file_path or self.DEFAULT_FILE_NAME)
        if not os.path.exists(file_path):
            return
        with open(file_path, "rb") as user_pool_file:
            user_pool = pickle.load(user_pool_file)
            self.users = user_pool.users
            self.ips = user_pool.ips

    def save(self, file_path=None):
        file_path = get_path(file_path or self.DEFAULT_FILE_NAME)
        with open(file_path, "wb") as user_pool_file:
            pickle.dump(self, user_pool_file)

    def add_user(self, user):
        existed_user = self.users.get(user.id)
        new_ips = user.ips
        if existed_user:
            new_ips -= existed_user.ips
            user.ips |= existed_user.ips

        self.users[user.id] = user

        for ip in new_ips:
            if ip: self.ips[ip] |= {user.id}

class Article:
    def __init__(self, content, url):
        self.url = url
        self.article = self.parse_article(content)
        self.pos_users, self.neu_users, self.nag_users = \
                self.parse_comments(content)

        author = User(content, "article", url)
        self.author = author.id

        print("[Url]: {}".format(url))
        print("[Author]: {}".format(self.author))
        print("[Article]:\n{}".format(self.article.replace("\n", "\n".ljust(12))))
        print("[Positive]: {}".format(", ".join(self.pos_users)))
        print("[Neutral]: {}".format(", ".join(self.neu_users)))
        print("[Nagitive]: {}".format(", ".join(self.nag_users)))

    def parse_article(self, content):
        main_paragraphs = content.find(id="main-content").find_all(string=RE_ARTICLE)
        return " ".join(paragraph.string for paragraph in main_paragraphs)

    def parse_comments(self, content):
        pos_users = []
        neu_users = []
        nag_users = []
        users = {
            "推": pos_users,
            "→": neu_users,
            "噓": nag_users,
        }

        for comment_html in content.find_all(class_="push"):
            comment_tag = comment_html.find(class_="push-tag").string.strip()
            user = User(comment_html)
            users[comment_tag].append(user.id)

        return pos_users, neu_users, nag_users

class ArticlePool:
    DEFAULT_FILE_NAME = "article_pool.pk"

    def __init__(self):
        self.articles = {}

    def load(self, file_path=None):
        file_path = get_path(file_path or self.DEFAULT_FILE_NAME)
        if not os.path.exists(file_path):
            return
        with open(file_path, "rb") as article_pool_file:
            self.articles = pickle.load(article_pool_file).articles

    def save(self, file_path=None):
        file_path = get_path(file_path or self.DEFAULT_FILE_NAME)
        with open(file_path, "wb") as article_pool_file:
            pickle.dump(self, article_pool_file)

    def add_article(self, article):
        self.articles[article.url] = article

class Progress:
    DEFAULT_FILE_NAME = "progress.pk"

    def __init__(self):
        self.current_index = 999

    def load(self, file_path=None):
        file_path = get_path(file_path or self.DEFAULT_FILE_NAME)
        if not os.path.exists(file_path):
            return
        with open(file_path, "rb") as progress_file:
            self.current_index = pickle.load(progress_file).current_index

    def save(self, file_path=None):
        file_path = get_path(file_path or self.DEFAULT_FILE_NAME)
        with open(file_path, "wb") as progress_file:
            pickle.dump(self, progress_file)
