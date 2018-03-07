#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据转换器，用于数据清洗
"""


class ItemTransformer(object):
    """
    数据转换器基类
    """

    def __init__(self):
        pass

    def transform(self, item=None, ops=None):
        """
        转换操作
        :param item: 原始数据项
        :return: 转换后数据项
        """
        if item is None:
            item = {}
        return item
