# -*- coding: utf-8 -*-
import sys

import re


import urllib
from bs4 import BeautifulSoup
from random import randint
import time
import json
import codecs


def used_pages_anjuke():
    home = 'http://shenzhen.anjuke.com/community/'
    response = urllib.request.urlopen(home)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    num = soup.select_one("span.tit em:nth-of-type(2)").string
    print(num)
    page_size = 30
    for p in range(1, int(num) / page_size + 2):
        if p == 1:
            page = 'http://shenzhen.anjuke.com/community/'
        else:
            page = 'http://shenzhen.anjuke.com/community/p{page_num}/'.format(page_num=p)
        print(page)
        yield page


def used_houses_by_page(page):
    response = urllib.request.urlopen(page)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    items = soup.select("div.li-itemmod")

    for item in items[0:30]:
        name = item.select_one("div.li-info h3 a").string
        address = item.select_one("address").string.strip()
        price = item.select_one("div.li-side p strong").string
        data_link = item['link']
        json_object = {"type": "USED", "name": name, "address": address, "price": int(price), "data_link": data_link}
        print(json_object)
        yield json_object


def boom_location(house):
    address = house['address']
    try:
        url = u'http://api.map.baidu.com/geocoder/v2/' \
              u'?ak=Q0ERGQ0nNRN9xUQs3kqiIK80PUF950zG&output=json&address=%s&city=深圳市' % address
        response = urllib.request.urlopen(url)
        json_object = json.loads(response.read())
        lat = json_object['result']['location']['lat']
        lon = json_object['result']['location']['lng']
        location = {"lat": lat, "lon": lon}
        print(location)
        return location
    except Exception:
        print("trans error in %s" % address)
        return {}


def boom_rate(house):
    link = house["data_link"]
    try:
        url = u'http://shenzhen.anjuke.com/' + link
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "lxml")
        plot_ratio = soup.select_one("dl.comm-r-detail.float-r dd:nth-of-type(4)").string
        plot_ratio = float(re.findall(r"\d+\.?\d*", plot_ratio)[0])
        greening_rate = soup.select_one("dl.comm-r-detail.float-r dd:nth-of-type(7)").string
        greening_rate = float(re.findall(r"\d+\.?\d*", greening_rate)[0])
        print(greening_rate)
        greening_rate = 0 if greening_rate >= 100 or greening_rate < 0 else greening_rate
        rate = {"plotRatio": plot_ratio, "greeningRate": greening_rate}
        print(rate)
        return rate
    except Exception:
        print("trans error in %s" % link)
        return {}


import pymongo
from pymongo import MongoClient

client = MongoClient('mongodb://10.40.100.16:27017/')
db = client.test

time_time = time.time()
origin_file = "d:/sz-used-house%s.txt" % time_time
pages = used_pages_anjuke()
for page in pages:
    time.sleep(randint(1, 5) / 5)
    houses = used_houses_by_page(page)
    for house in houses:
        time.sleep(randint(5, 50))
        rate = boom_rate(house)
        house = dict(house, **rate)  # 合并
        location = boom_location(house)
        house = dict(house, **location)  # 合并
        del house['data_link']
        print(house)
        f = open(origin_file, "a")
        f.write(json.dumps(house, ensure_ascii=False) + "\n")
        f.close()
        db.house.insert(house)
