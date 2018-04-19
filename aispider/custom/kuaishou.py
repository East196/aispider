#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -*-coding:utf-8-*-
# time: 2018.1.5
# author : Corleone
import urllib.request
import urllib.parse
import urllib.error
import json, os, re, socket, time, sys
import queue
import threading
import logging


def get_video():
    url = "http://101.251.217.210/rest/n/feed/hot?app=0&lon=121.372027&c=BOYA_BAIDU_PINZHUAN&sys=ANDROID_4.1.2&mod=HUAWEI(HUAWEI%20C8813Q)&did=ANDROID_e0e0ef947bbbc243&ver=5.4&net=WIFI&country_code=cn&iuid=&appver=5.4.7.5559&max_memory=128&oc=BOYA_BAIDU_PINZHUAN&ftt=&ud=0&language=zh-cn&lat=31.319303 "
    data = {
        'type': 7,
        'page': 2,
        'coldStart': 'false',
        'count': 20,
        'pv': 'false',
        'id': 5,
        'refreshTimes': 4,
        'pcursor': 1,
        'os': 'android',
        'client_key': '3c2cd3f3',
        'sig': '22769f2f5c0045381203fc57d1b5ad9b'
    }
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "kwai-android")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    params = urllib.parse.urlencode(data)
    try:
        html = urllib.request.urlopen(req, params).read()
    except urllib.error.URLError:
        logger.warning(u"网络不稳定 正在重试访问")
        html = urllib.request.urlopen(req, params).read()
    into_queue(html)


def into_queue(html):
    result = json.loads(html)
    reg = re.compile(u"[\u4e00-\u9fa5]+")  # 只匹配中文
    for x in result['feeds']:
        try:
            title = x['caption'].replace("\n", "")
            name = " ".join(reg.findall(title))
            video_q.put([name, x['photo_id'], x['main_mv_urls'][0]['url']])
        except KeyError:
            pass


def by_user():
    with open("d://kuaishou_video.txt","rb") as fp:
        lines = fp.read()
        lines = lines.decode("utf8","ignore")
        for i,line in enumerate(lines.splitlines()):
            if line:
                print(i,line[:20])
                into_queue(line)

def download(video_q):
    path = u"D:\快手2"
    while True:
        data = video_q.get()
        name = data[0].replace("\n", "")
        id = data[1]
        url = data[2]
        file = os.path.join(path, name + ".mp4")
        logger.info(u"正在下载：%s" % name)
        try:
            urllib.request.urlretrieve(url, file)
        except IOError:
            file = os.path.join(path, u"神经病呀" + '%s.mp4') % id
            try:
                urllib.request.urlretrieve(url, file)
            except (socket.error, urllib.error.ContentTooShortError):
                logger.warning(u"请求被断开，休眠2秒")
                time.sleep(2)
                urllib.request.urlretrieve(url, file)

        logger.info(u"下载完成：%s" % name)
        video_q.task_done()


def main():
    # 使用帮助
    try:
        # threads = int(sys.argv[1])
        threads = 3
    except (IndexError, ValueError):
        print(u"\n用法: " + sys.argv[0] + u" [线程数:10] \n")
        print(u"例如：" + sys.argv[0] + " 10" + u"  爬取视频 开启10个线程 每天爬取一次 一次2000个视频左右(空格隔开)")
        return False
    # 判断目录
    if os.path.exists(u'D:\快手') == False:
        os.makedirs(u'D:\快手')
    # 解析网页
    logger.info(u"正在爬取网页")
    for x in range(1, 2):
        logger.info(u"第 %s 次请求" % x)
        get_video()
    num = video_q.qsize()
    logger.info(u"共 %s 视频" % num)
    # 多线程下载
    for y in range(threads):
        t = threading.Thread(target=download, args=(video_q,))
        t.setDaemon(True)
        t.start()

    video_q.join()
    logger.info(u"-----------全部已经爬取完成---------------")


if __name__ == '__main__':
    # 日志模块
    logger = logging.getLogger("AppName")
    formatter = logging.Formatter('%(asctime)s %(levelname)-5s: %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.formatter = formatter
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    if os.path.exists(u'D:\快手2') == False:
        os.makedirs(u'D:\快手2')
    video_q = queue.Queue()  # 视频队列
    by_user()
    num = video_q.qsize()
    logger.info(u"共 %s 视频" % num)
    # 多线程下载
    for y in range(3):
        t = threading.Thread(target=download, args=(video_q,))
        t.setDaemon(True)
        t.start()
    video_q.join()
    logger.info(u"-----------全部已经爬取完成---------------")

# 分三个区域吧 queue+thread download get_video_urls_by_stream
# 自己加新区域 get_video_urls_by_user 读json文件获取url
# face 夜神模拟器找作者，获取列表，http://anyproxy.io/cn/，转发flask对接，后台直接爬视频，合成
