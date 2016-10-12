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
	
def test_defaultuser(user,password,need_idle,*args):
    try:
        MessageMapping.init()
        client = TestClient(user,password)
        resp = client.call_message_by_name(args[0],args[1],*args[2:]) 
        if need_idle:
            client.idle()
        print "== result ==>",resp.header.result
    except:
        traceback.print_exc()
    finally:
        pass
        
    
if __name__ == "__main__":
    if sys.argv[1] != "-w":
        test_defaultuser(sys.argv[1],"123456",False,*sys.argv[2:])
    else:
        test_defaultuser(sys.argv[2],"123456",True,*sys.argv[3:])
    print "Done"