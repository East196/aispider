#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urlparse
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


def get_json(url):
    r = requests.get(url, headers=headers)
    return r.json()


def get_domain(url):
    split = urlparse.urlsplit(url)
    domain = "{scheme}://{netloc}".format(scheme=split.scheme, netloc=split.netloc)
    return domain
