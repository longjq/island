#coding: utf-8
import logging
from services import *

import struct
import binascii

import traceback
import time

from access.accessserver import *
from message.base import *
from message.route import *

class AccessService(IService):
    def init(self):
        serverConfig = self.server.getServiceConfig(self.serviceId)
        ip = serverConfig.options["access_server_ip"]
        port = int(serverConfig.options["access_server_port"])
        access_server = AccessServer(self.serviceId,self.server.conf,ip,port)
        
        access_server.set_access_service(self)
        self.access_server = access_server
        
    # 处理从其它服务发送至AccessService的事件
    def onEvent(self,event):
        logging.info("access service OnEvent User=%d event_type=%d", event.param1, event.eventType)
        
        # 其余消息转发至客户端
        # event.param1 存放用户id，该消息不能小于等于0，否则丢弃
        # event.param2 存放对应事务id，如果小于0，则代表无对应消息 
       
        if event.eventType == E_SYSTEM_READY:
        	logging.info("Access Service Receive System Ready Event")
        	return
        if event.param1 >= 0 :
            # 用户消息返回了,event.param1 = userid and event.param2 = transaction,transaction < 0 means it's a event
            self.access_server.response_user_message(event.param1, event.param2, event.eventType,event.eventData)
        else:
            logging.error("event param1 < -1,so event should be discarded :eventType = %d,transaction=%d",event.eventType,event.tranId)
            return 
    
if __name__ == "__main__":
    pass


