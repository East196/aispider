#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib.request
import urllib.parse
import json


def open_url(url, page_num, keywords):
    try:
        # 设置post请求参数
        page_data = urllib.parse.urlencode([
            ('pn', page_num),
            ('kd', keywords)
        ])
        # 设置headers
        page_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
            'Connection': 'keep-alive',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Cookie': 'JSESSIONID=ABAAABAABEEAAJA8F28C00A88DC4D771796BB5C6FFA2DDA; user_trace_token=20170715131136-d58c1f22f6434e9992fc0b35819a572b; LGUID=20170715131136-13c54b92-691c-11e7-893a-525400f775ce; index_location_city=%E5%8C%97%E4%BA%AC; _gat=1; TG-TRACK-CODE=index_search; _gid=GA1.2.496231841.1500095497; _ga=GA1.2.1592435732.1500095497; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1500095497; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1500104021; LGSID=20170715143221-5b993c04-6927-11e7-a985-5254005c3644; LGRID=20170715153341-ec8dbfd2-692f-11e7-a989-5254005c3644; SEARCH_ID=d27de6042bdf4d508cf9b39616a98a0d',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://www.lagou.com/jobs/list_%E6%95%B0%E6%8D%AE%E6%8C%96%E6%8E%98?labelWords=&fromSearch=true&suginput=',
            'X-Anit-Forge-Token': 'None',
            'X-Requested-With': 'XMLHttpRequest'
        }
        # 打开网页
        req = urllib.request.Request(url, headers=page_headers)
        content = urllib.request.urlopen(req, data=page_data.encode('utf-8')).read().decode('utf-8')
        return content
    except Exception as e:
        print(str(e))


# 获取招聘职位信息
def get_position(url, page_num):
    try:
        page_content = open_url(url, page_num, keywords)
        data = json.loads(page_content)
        content = data.get('content')
        positionResult = content.get('positionResult').get('result')
        result = [('positionId', '职位ID'), ('positionName', '职位名称'), ('salary', '薪资'), ('createTime', '发布时间'), ('workYear', '工作经验'), ('education', '学历'),
                  ('positionLables', '职位标签'), ('jobNature', '职位类型'), ('firstType', '职位大类'), ('secondType', '职位细类'), ('positionAdvantage', '职位优势'),
                  ('city', '城市'), ('district', '行政区'), ('businessZones', '商圈'), ('publisherId', '发布人ID'), ('companyId', '公司ID'), ('companyFullName', '公司名'),
                  ('companyShortName', '公司简称'), ('companyLabelList', '公司标签'), ('companySize', '公司规模'), ('financeStage', '融资阶段'), ('industryField', '企业领域'),
                  ('industryLables', '企业标签')]

        if (len(positionResult) > 0):
            for position in positionResult:
                print(position)
                with open("lagou_position.txt", 'a', encoding="utf-8") as fh:
                    fh.write("---------------------------\n")
                for r in result:
                    with open("lagou_position.txt", 'a', encoding="utf-8") as fh:
                        fh.write(str(r[1]) + ":" + str(position.get(r[0])) + "\n")
        return len(positionResult)
    except Exception as e:
        print(str(e))


# 爬取拉勾网招聘职位信息
if __name__ == "__main__":
    # 爬取起始页
    city = urllib.parse.quote("深圳")
    url = 'https://www.lagou.com/jobs/positionAjax.json?city={city}&needAddtionalResult=false'.format(city=city)
    print(url)
    # 设置查询的关键词
    keywords = "CTO"
    page_num = 1
    while True:
        print("正在爬取第" + str(page_num) + "页......")
        result_len = get_position(url, page_num)
        if (result_len > 0):
            page_num += 1
        else:
            break
    print("爬取完成")
