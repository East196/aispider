#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据存储模块
"""
# TODO header数据准备
# TODO urls生成
# TODO url解数据返回单条或多条
# TODO 数据转换
# TODO 数据存储
from __future__ import print_function
import configparser

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

    def __init__(self, with_head=False):
        super(CsvSaver, self).__init__()
        self.with_head = with_head

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


class MongoSaver(DataSaver):
    """
    MongoDB专用存储器
    """

    def __init__(self):
        super(MongoSaver, self).__init__()
        from pymongo import MongoClient
        mongo_host = config.get("mongo", "host")
        mongo_dbname = config.get("mongo", "dbname")

        self.client = MongoClient(mongo_host)
        self.db = self.client.get_database(mongo_dbname)

    def save(self, table='test', items=None):
        """
        向集合存储批量数据
        :param table: 对应mongodb的collection
        :param items: 待插入的数据
        """
        if items is None:
            items = []
        self.db[table].insert_many(items)


class HBaseSaver(DataSaver):
    """
    HBase专用数据存储器
    """

    def __init__(self):
        super(HBaseSaver, self).__init__()
        import happybase
        host = config.get("hbase", "host")  # '10.40.100.16'
        table = config.get("hbase", "table")
        self.connection = happybase.Connection(host)
        self.table = self.connection.table(table)

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
    a, _ = (1, 2)
    print(a)
    a, _, c = (1, 2, 3)
    print(a)
    print(c)

    # db_saver = CsvSaver(with_head=True)  # HbaseSaver()  # MongoSaver()
    # db_saver.save(items=[{'uid': '888', 'name': 'tung', 'sex': 'True'},
    # {'uid': '666', 'name': 'snow', 'sex': 'False'}])
