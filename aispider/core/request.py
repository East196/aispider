#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urlsplit
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"
}


def get_soup(url):
    r = requests.get(url, headers=headers)
    print(r.content)
    soup = BeautifulSoup(r.content, "lxml")
    return soup


def get_comment_soup(url):
    r = requests.get(url, headers=headers)
    # print(r.content.decode("utf8"))
    html = r.content.decode("utf8").replace("<!--", "").replace("-->", "")
    soup = BeautifulSoup(html, "lxml")
    # print(soup.prettify())
    return soup


def get_json(url):
    r = requests.get(url, headers=headers)
    return r.json()


def get_domain(url):
    split = urlsplit(url)
    domain = "{scheme}://{netloc}".format(scheme=split.scheme, netloc=split.netloc)
    return domain
