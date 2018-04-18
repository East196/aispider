#!/usr/bin/env python
# -*- coding: utf-8 -*-


from selenium import webdriver
import time
import random


def get_mids(uid):
    browser.get("https://www.douyin.com/share/user/{uid}/?share_type=link".format(uid=uid))
    items = browser.find_elements_by_css_selector("ul.list li.item")
    for item in items:
        print(item.get_attribute("data-id"))
# 抖音现在通过share user查mid多了个参数，不过这个selenium可以搞定。但是无法通过share mid获取视频了好像...

if __name__ == '__main__':
    browser = webdriver.Firefox()
    browser.maximize_window()

    get_mids("79292277572")

    browser.close()
