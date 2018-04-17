#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aispider.crawler.auto_crawler import *
import os


def get_chapter(url):
    soup = get_soup(url)
    chapter = soup.select_one("div.bookname > h1").get_text()
    content = soup.select_one("#content").get_text()
    return chapter, content


def novel_crawl(url):
    soup = get_soup(url)
    book_name = soup.select_one("head > meta[property='og:novel:book_name']").get("content")
    author = soup.select_one("head > meta[property='og:novel:author']").get("content")
    category = soup.select_one("head > meta[property='og:novel:category']").get("content")
    description = soup.select_one("head > meta[property='og:description']").get("content")
    txt_name = "../book/" + book_name + ".txt"
    with open(txt_name, "a") as fp:
        fp.write(book_name + os.linesep)
        fp.write(author + os.linesep)
        fp.write(category + os.linesep)
        fp.write(description + os.linesep)
    for href in soup.select("#list > dl > dd > a"):
        suburl = get_domain(url) + href.get('href')
        chapter, content = get_chapter(suburl)
        print(chapter, content)
        with open(txt_name, "a") as fp:
            fp.write(chapter + os.linesep)
            contents = content.split("    ")  # 分行
            for sub_content in contents:
                if len(sub_content):
                    fp.write(sub_content + os.linesep)

def rule_novel_crawl(url):
    doc = get_soup(url).prettify()
    print(len(doc))
    rule = """
    <root>
        <parse type='soup' name='head' cssselector='head' list='False'>
            <parse type='soup' name='book_name' cssselector='meta[property="og:novel:book_name"]' attr="content"/>
            <parse type='soup' name='author' cssselector='meta[property="og:novel:author"]' attr="content"/>
            <parse type='soup' name='category' cssselector='meta[property="og:novel:category"]' attr="content"/>
            <parse type='soup' name='description' cssselector='meta[property="og:description"]' attr="content"/> 
        </parse>
        
    </root>
    """
    doc_data = AutoCrawler().extract(doc, rule)
    print(doc_data[0][1])
    # TODO 加入<parse type='soup' name='chapters' cssselector='#list > dl > dd > a' attr="href" list="True"/>


if __name__ == '__main__':
    urls = list()
    urls.append('https://www.xxbiquge.com/0_494/')  # 大道争锋
    for url in urls:
        rule_novel_crawl(url)
