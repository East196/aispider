#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aispider.core.reqbase import *

r = requests.get("http://tieba.baidu.com/f?kw=哈士奇&ie=utf-8", headers=headers)
html = r.content.decode("utf8").replace("<!--", "").replace("-->", "")
soup = BeautifulSoup(html, "lxml")

topics, ties, rens = [s.text for s in soup.select("span.red_text")]
print("主题数：", topics)
print("帖子数：", ties)
print("人数：", rens)

for d in soup.select("li div.t_con"):
    print("回复数"+d.select_one("span.threadlist_rep_num").text)
    print("标题"+d.select_one(".threadlist_title a")["title"])
    print("网址"+d.select_one(".threadlist_title a")["href"])
