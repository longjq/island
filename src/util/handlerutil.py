#coding: utf-8

import logging
import traceback
from message.base import *
from db.connect import *
from config import var

import time

HOOK_BEFORE = []
HOOK_EXCEPTION = []
HOOK_FAILURE = []
HOOK_SUCCESS = []


def USE_TRANSACTION(func):
    def f(self,event):
        req,idx = get_request(event.eventData)
        session = None   
        resp = create_response(req)
        resp.header.result = 0
        begin_time = int(time.time()) 
        func_result = True
        try :
            session = Session()
            session.begin()
            
            stopped = False
            for hook_func in HOOK_BEFORE:
                if hook_func(session,req,resp,event) != 0:
                    stopped = True
                    break
            
            if not stopped:                    
                func_result = func(self,session,req,resp,event) 
            else:
                func_result = False                        
            
            if resp.header.result != 0:
                for hook_func in HOOK_FAILURE:
                    hook_func(session,req,resp,event)
                session.rollback()                    
            else:
                for hook_func in HOOK_SUCCESS:
                    hook_func(session,req,resp,event)
                session.commit()
                
        except:
            logging.exception("服务调用出现异常")
            resp.header.result = -1
            for hook_func in HOOK_EXCEPTION:
                hook_func(session,req,resp,event)
            session.rollback()
        finally:
            if session != None:
                session.close()
                session = None    
        
        event_data = resp.encode()
        if func_result != False:    
            self.server.sendEvent(event_data, self.serviceId, event.srcId, resp.header.command, event.param1, event.param2)
    return f

"""
def USE_SESSION(func):
    def f(self,event):
        req,idx = get_request(event.eventData)
        
        session = None   
        resp = create_response(req)
        resp.header.result = 0
        begin_time = int(time.time()) 
        func_result = True
        try :
            session = Session()
            func_result = func(self,session,req,resp,event)              
        except:
            logging.exception("服务调用出现异常")
            resp.header.result = -1
        finally:
            if session != None:
                session.close()
                session = None    
        event_data = resp.encode()
        if var.DEBUG:
            logging.info("event_data : " + str(resp))
            #logging.info("event type %d,time effort %d,",req.header.command, int(time.time()) - begin_time)    
        if func_result != False: 
            self.server.sendEvent(event_data, self.serviceId, event.srcId, resp.header.command, event.param1, event.param2)
    return f
    
def HANDLER(func):
    def f(self,event):
        req,idx = get_request(event.eventData)
        session = None   
        resp = create_response(req)
        resp.header.result = 0
        begin_time = int(time.time()) 
        func_result = True
        try :
            func_result = func(self,req,resp,event)        
            
        except:
            logging.exception("服务调用出现异常")
            resp.header.result = -1 
        event_data = resp.encode()
        if var.DEBUG:
            logging.info("event_data : " + str(resp))
            #logging.info("event type %d,time effort %d,",req.header.command, int(time.time()) - begin_time)    
        if func_result != False:
            self.server.sendEvent(event_data, self.serviceId, event.srcId, resp.header.command, event.param1, event.param2)
    return f  
"""

# 用于测试模式
if var.UNIT_TEST:
    def USE_TRANSACTION(func):
        return func