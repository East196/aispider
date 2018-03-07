# -*- coding: utf-8 -*-


import re

import urllib
from bs4 import BeautifulSoup
from random import randint
import time
import json
import codecs


def pages_anjuke():
    home = 'http://sz.fang.anjuke.com/loupan/all/'
    soup = get_soup(home)
    num = soup.select_one("span.result em").string
    size = 30
    page_nums = range(1, int(num) / size + 2)
    for page_num in page_nums:
        if page_num == 1:
            page = 'http://sz.fang.anjuke.com/loupan/all/'
        else:
            page = 'http://sz.fang.anjuke.com/loupan/all/p{page_num}/'.format(page_num=page_num)
        print(page)
        yield page


def houses_by_page(page):
    soup = get_soup(page)
    items = soup.find_all('div', "item-mod", rel='nofollow')
    for item in items[0:30]:
        name = item.select_one("a.items-name").string
        address = item.select_one("a.list-map").string
        tag = item.find("p", "price")
        data_link = item['data-link']

        if tag is None:
            price = 0
        else:
            price = int(tag.span.string)
        json_object = {"type": "NEW", "name": name, "address": address, "price": price, "data_link": data_link}
        print(json_object)
        yield json_object


def get_soup(page):
    response = urllib.request.urlopen(page)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    return soup


def get_json_object(url):
    response = urllib.request.urlopen(url)
    json_object = json.loads(response.read())
    return json_object


def houses_activiti():
    pages = pages_anjuke()
    houses = []  # flatMap
    for page in pages:
        for house in houses_by_page(page):
            houses.append(house)
    houses = filter(lambda house: house['address'].find(u"深圳周边") == -1, houses)
    houses = map(boom_location, houses)
    houses = map(boom_rate, houses)
    return houses


def del_field(item, field_name):
    del item[field_name]


def trans_field(item, field_name, func):
    trans = func(item[field_name])
    item = dict(item, **trans)  # 合并
    return item


def filter_item(item, field_name, func):
    if func(item, field_name):
        return None
    return item


def filter_by_address(item, field_name):
    return item[field_name] == -1


def boom_location(house):
    address = house['address']
    try:
        url = u'http://api.map.baidu.com/geocoder/v2/' \
              u'?ak=Q0ERGQ0nNRN9xUQs3kqiIK80PUF950zG&output=json&address=%s&city=深圳市' % address
        json_object = get_json_object(url)
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
        url = link.replace(u'http://sz.fang.anjuke.com/loupan/', u'http://sz.fang.anjuke.com/loupan/canshu-') \
            .replace(u'.html', u'.html?from=loupan_index_more')
        soup = get_soup(url)
        plot_ratio = soup.select_one(
            "#container > div.can-container.clearfix > div.can-left > div:nth-of-type(3) > div.can-border >"
            " ul > li:nth-of-type(4) > div.des").text.replace(
            "住宅：", "").replace("[查看详情]", "").strip()
        plot_ratio = float(re.findall(r"\d+\.?\d*", plot_ratio)[0])
        greening_rate = soup.select_one(
            "#container > div.can-container.clearfix > div.can-left > div:nth-of-type(3) > div.can-border >"
            " ul > li:nth-of-type(5) > div.des").text.replace(
            "[查看详情]", "").strip().replace("%", "")
        greening_rate = float(re.findall(r"\d+\.?\d*", greening_rate)[0])
        greening_rate = 0 if greening_rate >= 100 or greening_rate < 0 else greening_rate
        rate = {"plotRatio": plot_ratio, "greeningRate": greening_rate}
        print(rate)
        return rate
    except Exception:
        print("trans error in %s" % link)
        return {}

if __name__ == '__main__':

    time_time = time.time()
    file_name = "d:/sz-new-house-%s.txt" % time_time
    pages = pages_anjuke()
    for page in pages:
        time.sleep(randint(1, 2) / 5)
        houses = houses_by_page(page)
        for house in houses:
            rate = boom_rate(house)
            house = dict(house, **rate)  # 合并
            location = boom_location(house)
            house = dict(house, **location)  # 合并
            del house['data_link']
            f = open(file_name, "a")
            f.write(json.dumps(house, ensure_ascii=False) + "\n")
            f.close()
