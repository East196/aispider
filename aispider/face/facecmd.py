#!/usr/bin/env python
# -*- coding: utf-8 -*-


import itchat


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    print(msg)
    if msg['Text'].startswith("http"):
        print(msg['Text'])
    return msg['Text']


itchat.auto_login(hotReload=True)

itchat.send('Hello, filehelper', toUserName='filehelper')
itchat.run()
