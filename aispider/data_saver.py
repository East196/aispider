#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据存储模块,按照大数据存储惯例，只增加不更新
"""

import configparser
import json
from lxml import etree

from pymongo.errors import BulkWriteError

config = configparser.ConfigParser()
config.read("data_saver.conf")


class DataSaver(object):
    """
    通用存储器
    """

    def __init__(self):
        pass

    def save(self, table='test', items=None):
        """
        通用存储方法
        :param table: 存储表名/集合
        :param items: 待存储的数据
        """
        pass


class CsvSaver(DataSaver):
    """
    CSV文件专用存储器
    """

    def __init__(self, with_head=None):
        super(CsvSaver, self).__init__()
        if not with_head:
            self.with_head = False
        else:
            self.with_head = True

    def save(self, table='test.csv', items=None):
        """
        向csv文件存储items
        :param table: 对应CSV文件的文件名
        :param items: 待插入的数据
        """
        if items is None:
            items = []
        lines = [','.join([value for key, value in item.items()]) + '\n'
                 for item in items]
        if self.with_head:
            head = ','.join([key for key, value in items[0].items()]) + '\n'
            lines = [head] + lines
        with open(table, 'w') as fp:
            fp.writelines(lines)


class JsonSaver(DataSaver):
    """
    Json专用存储器
    """

    def __init__(self, ensure_ascii=False):
        super(JsonSaver, self).__init__()
        self.ensure_ascii = ensure_ascii

    def save(self, table='test.json', items=None):
        """
        向json文件存储items
        :param table: 对应json文件的文件名
        :param items: 待插入的数据
        """
        if items is None:
            items = []
        lines = [json.dumps(item, ensure_ascii=self.ensure_ascii) + '\n' for item in items]
        with open(table, 'w') as fp:
            fp.writelines(lines)


class MongoSaver(DataSaver):
    """
    MongoDB专用存储器
    """

    def __init__(self, host="10.40.100.16", database_name='test'):
        super(MongoSaver, self).__init__()
        from pymongo import MongoClient
        self.client = MongoClient(host)
        self.db = self.client.get_database(database_name)

    def save(self, table='test', items=None):
        """
        向集合存储批量数据
        :param table: 对应mongodb的collection
        :param items: 待插入的数据
        """
        if items is None:
            items = []
        if items and items[0].get('uid'):
            items = [dict(item, **{"_id": item['uid']}) for item in items]
        try:
            self.db[table].insert_many(items)
        except BulkWriteError as bwe:
            print(bwe.details)
            # you can also take this component and do more analysis
            write_errors = bwe.details['writeErrors']
            print(write_errors)
            pass


class HBaseSaver(DataSaver):
    """
    HBase专用数据存储器
    """

    def __init__(self, host="10.40.100.16", table_name='test'):
        super(HBaseSaver, self).__init__()
        import happybase
        self.connection = happybase.Connection(host)
        self.table = self.connection.table(table_name)

    def save(self, table='test', items=None):
        """
        向HBase表存储批量数据
        :param table: 对应HBase的表名
        :param items: 待插入的数据
        """
        if items is None:
            items = []
        print(self.connection.tables())

        # 判断表是否存在，如果不存在则创建
        if table not in self.connection.tables():
            print('create table')
            self.connection.create_table(table, {'info': dict(), 'stat': dict()})
        else:
            print('keep table')
        families = [key for key, _ in self.table.families().items()]
        print(families)

        key_generator = get_row_generator(table)
        key_data = {key_generator(item): HBaseSaver.family_item(families, item) for item in items}

        print(key_data)
        for key, data in key_data.items():
            self.table.put(key, data)

        print(self.table.row('888'))

    @staticmethod
    def family_item(families, item):
        """
        将item的所有key转换为family：key的格式
        :param families: table的所有families
        :param item: 待传入的原始数据
        :return: key改变后的准备放入hbase的数据
        """
        return {HBaseSaver.family_key(families, key): value for key, value in item.items()}

    @staticmethod
    def family_key(families, key):
        """
        将key转换为family：key的格式
        :param families: table的所有families
        :param key: 待传入的key
        :return: 改变后的key
        """
        for family in families:
            if key.startswith(family + '_'):
                key[len(family)] = ':'
                return key
        return '%s:%s' % (families[0], key)


def get_uid(item):
    """
    获取item的uid
    :param item: item数据，dict型
    :return: item的uid
    """
    return item.get('uid')


def get_row_generator(table):
    """
    获取table的row key生成器，一般定义在项目主包下
    :param table: table name
    :return: table的row key生成器
    """
    generators = {
        'test': get_uid
    }
    return generators.get(table)


if __name__ == '__main__':
    items = [{'uid': '188', 'name': 'tung', 'nick': '嘎', 'sex': 'True'},
             {'uid': '666', 'name': 'snow', 'nick': '胖', 'sex': 'False'}]
    db_rule = '''
    <root>
        <to type='mongodb' host='mongodb://10.40.100.16:27017/' database_name='test' collection_name='test'/>
        <to type='hbase' host='10.40.100.16' table='test'/>
        <to type='csv' file_name='test.csv' />
        <to type='json' file_name='test.json' />
    </root>
    '''

    root = etree.XML(db_rule)
    targets = [child for child in root if child.tag == 'to']
    for target in targets:
        # TODO kwargs是不是好看点
        if target.get('type') == 'mongodb':
            host = target.get('host', '10.40.100.16')
            database_name = target.get('database_name', 'test')
            collection_name = target.get('collection_name', 'test')
            data_saver = MongoSaver(host=host, database_name=database_name)
            data_saver.save(table=collection_name, items=items)
        if target.get('type') == 'hbase':
            host = target.get('host', '10.40.100.16')
            table_name = target.get('table_name', 'test')
            data_saver = HBaseSaver(host=host, table_name=table_name)
            data_saver.save(table=table_name, items=items)
        if target.get('type') == 'csv':
            with_head = target.get('with_head')
            file_name = target.get('file_name', 'test.csv')
            data_saver = CsvSaver(with_head=with_head)
            data_saver.save(table=file_name, items=items)
        if target.get('type') == 'json':
            file_name = target.get('file_name', 'test.csv')
            data_saver = JsonSaver()
            data_saver.save(table=file_name, items=items)



            # data_saver = JsonSaver()
            # data_saver = CsvSaver(with_head=True)
            # data_saver = HbaseSaver()
            # data_saver = MongoSaver()
            # data_saver.save(items=items)
