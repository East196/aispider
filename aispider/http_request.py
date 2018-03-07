#!/usr/bin/env python
# -*- coding: utf-8 -*-


import configparser
import http.cookiejar
import json
import urllib
from time import sleep

import binascii
import pyDes
from bs4 import BeautifulSoup


class ConfigAccountProvider(object):
    def __init__(self, path="F:\cje\influence.conf"):
        self.config = configparser.ConfigParser()
        self.config.read(path)
        self.k = pyDes.des("8888", pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)

    def delete_all(self, account_type='weibo'):
        pass

    def update(self, account_type, username_password={}):
        pass

    def find_all(self, account_type='weibo'):
        accounts = []
        if account_type == 'weibo':
            username = self.config.get("weibo", "username")
            password = self.config.get("weibo", "password")
        else:
            username = self.config.get("qq", "username")
            password = self.config.get("qq", "password")
        print(password)
        password = self.k.decrypt(binascii.unhexlify(password))
        accounts.append({"username": username, "password": password})
        return accounts


class HttpRequest(object):
    """
    Http请求的一个简单封装，预处理header和cookie，同时设计处理http的异常
    """

    # TODO cookie_jar管理
    # TODO 使用kwargs&默认值
    def __init__(self, delay=1, cookie_jar=None):
        """
        :type delay: int
        """
        if cookie_jar is None:
            provider = ConfigAccountProvider()
            cookie_jar_provider = WeiboCookieJarProvider(provider.find_all())
            self.cookie_jar = cookie_jar_provider.get_random()
        else:
            self.cookie_jar = http.cookiejar.LWPCookieJar()
        cookie_support = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
        http_headers = [('User-agent', 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0')]
        opener.addheaders = http_headers
        urllib.request.install_opener(opener)
        self.delay = delay

    def get_html(self, url):
        """
        获取url页面内容
        :param url: 页面url
        :return: 页面内容
        """
        sleep(self.delay)
        html_document = urllib.request.urlopen(url).read()
        return html_document

    def get_json(self, url):
        """
        获取url页面的json表示
        :param url: 页面url
        :return: 使用dict表示的json
        """
        sleep(self.delay)
        json_document = urllib.request.urlopen(url).read()
        return json.loads(json_document)

    def get_soup(self, url):
        """
        获取url页面的BeautifulSoup表示
        :param url: 页面url
        :return: 使用BeautifulSoup表示的节点树
        """
        sleep(self.delay)
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "lxml")
        return soup


if __name__ == '__main__':
    request = HttpRequest()
    print(request.get_html("http://www.baidu.com"))
    print(request.cookie_jar.as_lwp_str())
