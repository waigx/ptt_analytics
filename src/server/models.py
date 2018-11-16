#!/usr/bin/env python

import pickle
import os
import re

RE_IP = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

class User:
    def __init__(self, content, content_type="comment", addr=None):
        id, ip = self.parse_user(content, content_type, addr)
        self.id = id
        self.ips = {ip}
        print("ID: {:<32} from IP: {}".format(id, ip))

    def parse_user(self, content, content_type, addr):
        def get_ip_from_text(text):
            match_obj = RE_IP.search(ip_container.string)
            return match_obj.group() if match_obj else ""

        if content_type == "comment":
            id = content.find(class_="push-userid").string.split()[0]
            ip_container = content.find(class_="push-ipdatetime").string
            ip = get_ip_from_text(ip_container.string)
        elif content_type == "article":
            id = content.find(class_="article-meta-value").string.split()[0]
            addr_container = content.find(string=addr)
            if addr_container:
                ip = get_ip_from_text(addr_container.parent.parent.previous_sibling.string)
            else:
                ip = ""
        return str(id), str(ip)

class UserPool:
    DEFAULT_FILE_NAME = "user_pool.pk"

    def __init__(self):
        self.users = {}
        self.ips = {}

    def __get_path(self, file_path):
        if not file_path:
            file_path = self.DEFAULT_FILE_NAME
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.path.dirname(__file__), file_path)
        return file_path

    def load(self, file_path=None):
        file_path = self.__get_path(file_path)
        if not os.path.exists(file_path):
            return
        with open(file_path, "rb") as user_pool_file:
            user_pool = pickle.load(user_pool_file)
            self.users = user_pool["users"]
            self.ips = user_pool["ips"]

    def save(self, file_path=None):
        with open(self.__get_path(file_path), "wb") as user_pool_file:
            pickle.dump({"users": self.users, "ips": self.ips}, user_pool_file)

    def add_user(self, user):
        existed_user = self.users.get(user.id)
        new_ips = user.ips
        if existed_user:
            new_ips -= existed_user.ips
            user.ips |= existed_user.ips

        self.users[user.id] = user

        for ip in new_ips:
            self.ips[ip] = user.id

