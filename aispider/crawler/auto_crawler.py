#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬取器
"""

from __future__ import print_function
import re
import json
from xml.sax.saxutils import escape

from lxml import etree
from bs4 import BeautifulSoup

from aispider.http_request import HttpRequest


class AutoCrawler(object):
    """
    自动爬取器，从xml rule中读取任务执行
    """

    def __init__(self, http_request=None):
        if http_request is None:
            self.http_request = HttpRequest()
        else:
            self.http_request = http_request

    def crawl(self, url, rule=None):
        """
        爬取操作
        :param url: 页面url
        :param rule: 页面解析rule的定义XML文档
        :type rule: string
        :return: 提取对象
        :rtype: dict
        """
        if rule is None:
            print("rule must be set")
        html = self.http_request.get_html(url)
        return self.extract(html, rule)

    def extract(self, html, rule):
        """
        根据rule指定的抓取规则，从页面内容中提取所需的对象
        :param html: 原始内容
        :param rule: 抓取规则
        :type rule: string
        :return: 提取对象
        :rtype: dict
        """
        doc = html.replace('\n', '')
        doc_data = (doc, {})
        root = etree.XML(rule)
        for child in root:
            print(child.tag, child.attrib['type'])
            doc_data = [sub for sub in get_doc(child, doc_data)]
        return doc_data

    def urls(self, url_template="http://www.baidu.com", **kwargs):
        # TODO 2 or 3 list
        # TODO 使用pop强化kwargs的限定
        """
        从url模板获取urls
        :param url_template: url模板
        :param kwargs: url定义的
        """
        for list_item in self._get_list_arg(kwargs)[1]:
            sub_kwargs = dict(kwargs)
            sub_kwargs['page'] = list_item
            yield url_template.format(**sub_kwargs)

    @staticmethod
    def _get_list_arg(kwargs):
        for key, value in kwargs.items():
            if type(value) is list:
                return key, value


def get_doc(root, doc_data):
    """
    :type root: beautifulsoup对象
    :param root: 上层解析器xml的结点
    :param doc_data: 是一个元组，第一个doc代表传入数据，第二个代表输出数据
    :return:是一个元组，第一个doc代表传入数据，第二个代表输出数据
    """
    if root.tag != 'parse':
        return
    if type(doc_data) != list:
        doc_data = [doc_data]
    # TODO 带第二参数，一直传第二参数内的数据
    if root.attrib['type'] == 'json':
        print("json")
        print(doc_data)
        for sub_doc, data in doc_data:
            sub_doc_json = json.loads(sub_doc.strip())
            # TODO 目前只有1级，TODO多级的jsonpath
            jsonpath = root.attrib['jsonpath']
            yield sub_doc_json.get(jsonpath), data
    if root.attrib['type'] == 're':
        print("re")
        print(doc_data)
        for sub_doc, data in doc_data:
            for item in re.findall(root.attrib['restr'], sub_doc):
                print("re :" + str(item))
                if root.attrib['name']:
                    data = dict(data, **{root.attrib['name']: "ok"})
                yield item.replace('\n', '').strip(), data
    if root.attrib['type'] == 'soup':
        print("soup")
        print(doc_data)
        for sub_doc, data in doc_data:
            print(sub_doc, data)
            soup = BeautifulSoup(sub_doc, 'lxml')
            cssselector = root.attrib['cssselector']
            print(cssselector)
            if root.attrib['list'] == 'False':
                print("list false")
                yield soup.select_one(cssselector).string, data
            if root.attrib['list'] == 'True':
                print("list true")
                for a in soup.select(cssselector):
                    if root.attrib['name']:
                        data = dict(data, **{root.attrib['name']: a.get_text()})
                    if len(root):
                        items = item_extract(a, root)
                        data = dict(data, **items)
                        yield data, data
                    else:
                        yield a.get_text(), data


def item_extract(soup, root):
    """
    :param soup:上层html数据的soup
    :param root:上层解析器xml的结点
    :return: 根据解析器抽取的items
    """
    items = {}
    for child in root:
        if child.tag != 'parse':
            continue
        if child.attrib['type'] == 'soup':
            sub_cssselector = child.attrib['cssselector']
            print(soup, sub_cssselector)
            items[child.attrib['name']] = soup.select_one(sub_cssselector).string
    return items


if __name__ == '__main__':
    crawler = AutoCrawler()
    for url in crawler.urls(url_template="http://a.b.cn/{type}?page={page}", page=[1, 2, 3], type=1):
        print(url)

    print(escape("<script>FM.view\((.+?)\);</script>"))
    rule = '''
    <root>
        <parse type='re' restr="%s" name='abc' list='True' />
        <parse type='json' jsonpath='jjj' list='False'/>
        <parse type='soup' name='aname' cssselector='div' list='True'>
            <parse type='soup' name='sub' cssselector='a.sub'/>
            <parse type='soup' name='sup' cssselector='a.sup'/>
        </parse>
    </root>
    ''' % escape("<script>FM.view\((.+?)\);</script>")

    doc = """<script>FM.view(
    {"jjj":"<div>1<a class='sub' href='a.html'>111</a><a class='sup' href='a.html'>222</a></div>
    <div>1<a class='sub' href='a.html'>111</a><a class='sup' href='a.html'>222</a></div>","xxx":2}
    );</script>"""
    doc_data = AutoCrawler().extract(doc, rule)
    for d in doc_data:
        print(1, 1, d)
