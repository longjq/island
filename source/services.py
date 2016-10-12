#coding: utf-8
import gevent
from gevent.queue import Queue

import struct
import logging
import time
from random import randint
import random
import traceback

from message.base import *
from message.route import *


# 该类为所有服务类的基类
# 每个服务运行于一个独立的线程中，系统保证onEvent是线程安全的函数

E_SYSTEM_READY = 99999

_quit_svc = object()

class BaseService:
    # 构造函数，一般情况下用户服务不需要定义自己的构造函数，可通过定义的init()函数实现初始化功能
    # 如服务定义自己的构造函数，则需要调用本类的__init__函数
    # server为服务器对象实例
    # serviceId为自身的服务标识
    # qSize为消息队列的长度，超出该队列长度的消息，将被丢弃
    def __init__(self,server,serviceId,thread_num = 1):
        self.server = server 
        self.queue = Queue()
        self.serviceId = serviceId
        for _ in xrange(thread_num):
            gevent.spawn(self._run)
        self.init()
    
    # 服务器在收到事件后，会调用该方法把事件放入队列中
    # 队列满时则不能存放新的消息，并抛出异常
    # 用户服务不能重定义该方法
    def dispatch(self,event):
        try:
            #logging.info("queue size:%s",self.queue.qsize())
            self.queue.put_nowait(event)
        except:
            logging.exception("服务发生异常")
        #logging.info("is full: %s",self.queue.full())
    
        
    # 初始化函数，服务可以通过重新定义该方法来完成初始化工作
    def init(self):
        pass    
    
    def sendEvent(self,eventData,dstId=-1,eventType=-1,param1=-1,param2=-1):           
		self.server.sendEvent(eventData,self.serviceId,dstId,eventType,param1,param2)
    
    # 用户服务需要重新定义该方法，实现自己的逻辑
    def onEvent(self,event):
        pass
    
    def stop(self):
        pass

    def _run(self):
        while True:
            try:
                msg = self.queue.get()
                if msg == _quit_svc:
                    break
                self.onEvent(msg)
            except:
                logging.exception("事件处理发生异常(onEvent)")


    def getServiceConfig(self):
        return self.server.getServiceConfig(self.serviceId)

    def getServerConfig(self):
        return self.server.getMyselfConfig()

    def getConfigOption(self,key,default_value):
        options = self.getServiceConfig().options
        if key in options:
            return options[key]
        else:
            return default_value
            
	# 转发用户事件至其它服务
    def forward_message(self,header,data):
    	dst_id = ROUTE.get_any_service(self.server,header)
    	if dst_id == None:
    	    logging.info("No service handler for %d" % header.command)
    	    return 
        self.server.sendEvent(data,self.serviceId,dst_id,header.command,header.user,header.transaction)
    
    def forward_message_directly(self,dst_id,event_type,user,transaction,data):    	
        self.server.sendEvent(data,self.serviceId,dst_id,event_type,user,transaction)
    
    # 广播该事件至所有消息的所有服务 
    def broadcast_message(self,header,data):
    	ids = ROUTE.get_all_service(self.server,header)
    	if ids == None:
    	    logging.info("No service handler for %d" % header.command)
    	    return 
    	for dst_id in ids:
            self.server.sendEvent(data,self.serviceId,dst_id,header.command,header.user,header.transaction)

    def send_client_event(self,access_server_id,user,event_type,data):
        pkg = struct.pack("llh" + str(len(data)) + "s",user,-1,event_type,data)
        self.server.redis.lpush("queue"+str(access_server_id),pkg)


class IMultiTaskService(BaseService):
    def __init__(self,server,serviceId,thread_num = 5):
        self.event_handlers = {}
        BaseService.__init__(self,server,serviceId,thread_num)
        

class GameService(IMultiTaskService):
    def registe_command(self,req,resp,handler):
        MessageMapping.set_message_handler(req.DEF.Value("ID"),self.__class__.__name__)
        self.event_handlers[req.ID] = handler
    
    def onEvent(self, event):
        event_type = event.eventType
        if event_type not in self.event_handlers:
            logging.info(" No valid event handler for event:%d", event_type)
            return 
        handler = self.event_handlers[event_type]
        try :
            handler(event)
        except:
            logging.exception("Error Is Happend for event %d", event_type)    

    

class IService(BaseService):
    def __init__(self,server,serviceId,qSize = 1024):
        BaseService.__init__(self,server,serviceId,qSize)
        

        
class TestService(IService):
    def init(self):
        self.count = 1
        
    def onEvent(self,event):
        self.count = self.count + 1
        event_data = "Hi,Hello TestClient : %d" % self.count
        if event.srcId >= 0:
            self.server.sendEvent(event_data,self.serviceId,event.srcId,100,event.param1,event.param2)
        