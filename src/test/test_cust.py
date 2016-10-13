#coding: utf-8
'''
Created on 2012-2-20

@author: Administrator
'''

from gevent import monkey;monkey.patch_all()

import importlib
import time,traceback
import threading
import sys,logging

from db.connect import *
from message.base import *
import socket

from proto.access_pb2 import *
from proto.constant_pb2 import *
from testbase import *

# 测试程序（用户名，密码，完成后是否退出（true=不断开来句），请求中的参数）
def test_defaultuser(user,password,need_idle,*args):
    try:
        # 初始化映射？todo...?
        MessageMapping.init()

        # 初始化测试实例
        client = TestClient(user,password)
        # 发送信息（服务名，接口名，*参数数组）
        resp = client.call_message_by_name(args[0],args[1],*args[2:])
        # client.ljq()
        if need_idle:
            # 不断开连接，维护连接，如果有消息，并会打印出来
            client.idle()
        # print "== result ==>",resp.header.result
    except:
        traceback.print_exc()
    finally:
        pass
        
    
if __name__ == "__main__":
    # 自定义-w功能，传入：代表程序运行完不退出，不传入：代表程序运行完直接退出
    if sys.argv[1] != "-w":
        # 退出方式启动测试程序
        test_defaultuser(sys.argv[1],"123456",False,*sys.argv[2:])
    else:
        # 不退出方式启动测试程序
        test_defaultuser(sys.argv[2],"123456",True,*sys.argv[3:])
    print "Done"