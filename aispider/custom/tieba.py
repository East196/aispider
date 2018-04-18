#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from aispider.core.request import *


def md5(s):
    import hashlib
    hl = hashlib.md5()
    hl.update(s.encode(encoding='utf-8'))
    return hl.hexdigest()


def tieba_summary(tieba_name):
    tieba_url = "http://tieba.baidu.com/f?kw={tieba_name}&ie=utf-8".format(tieba_name=tieba_name)
    soup = get_comment_soup(tieba_url)
    topics, ties, rens = [s.text for s in soup.select("span.red_text")]
    print("主题数：", topics)
    print("帖子数：", ties)
    print("人数：", rens)
    return int(topics), int(ties), int(rens)


def tieba_article_ids(tieba_name, req_num_min=1000):
    topics, ties, rens = tieba_summary(tieba_name)
    is_today = 1
    pn = 0
    while pn < topics and is_today is 1:
        pn_url = "http://tieba.baidu.com/f?kw={tieba_name}&ie=utf-8&pn={pn}".format(tieba_name=tieba_name, pn=pn)
        soup = get_comment_soup(pn_url)
        for d in soup.select("li div.t_con"):
            if d.select_one(".icon-top"):
                continue
            print(d.prettify())
            title = d.select_one(".threadlist_title a")["title"]
            href = d.select_one(".threadlist_title a")["href"]
            req_num = int(d.select_one("span.threadlist_rep_num").text)
            reply = d.select_one(".j_reply_data").text.strip()
            print("回复数", req_num)
            print("标题", title)
            print("网址", href)
            print("最后回复时间", reply)
            if ":" not in reply:
                is_today = 0
            if req_num > req_num_min:
                _, article_id = os.path.split(href)
                yield reply, title, article_id
        pn += 50


def article_lines(article_id):
    article_url = "http://tieba.baidu.com/p/{article_id}".format(article_id=article_id)
    soup = get_comment_soup(article_url)
    title = soup.select_one(".core_title h1")["title"]
    yield "## " + title
    for item in soup.select(".pb_content #j_p_postlist .j_l_post")[:1]:
        contents = item.select_one("cc .j_d_post_content").contents
        for content in contents:
            if not content:
                continue
            soup = BeautifulSoup(str(content), "lxml")
            if soup.select("img"):
                for img in soup.select("img"):
                    src = img["src"]
                    path = urlsplit(src).path
                    name = md5(src)
                    ext = os.path.splitext(path)[1] if os.path.splitext(path)[1] else ".jpg"
                    file_path = article_id + "/" + name + ext
                    download(src, file_path)
                    mdimg = "![{name}]({file_path})".format(name=name, file_path=file_path)
                    line = str(content).strip().replace(str(img.prettify()).strip(), mdimg)
                    yield line
            else:
                yield str(content).strip()


def download(src, file_path):
    file_dir, file_name = os.path.split(file_path)
    if file_dir and not os.path.exists(file_dir):
        os.makedirs(file_dir)
    pic = requests.get(src)
    with open(file_path, 'wb') as fp:
        fp.write(pic.content)


if __name__ == '__main__':
    article_ids = list(tieba_article_ids("猫", 1000))
    print(article_ids)

    for reply, title, article_id in article_ids:
        if ":" not in reply:
            continue
        with open("{reply}_{title}.md".format(reply=reply.replace(":","h"), title=title), "w", encoding="utf-8") as fp:
            lines = article_lines(article_id)
            for line in lines:
                print(line)
                fp.write(line + "\n\n")
