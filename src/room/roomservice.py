#coding: utf-8

import json
import logging
import traceback
import gevent

import binascii
from ctypes import *
from sqlalchemy.sql import select, update, delete, insert, and_, subquery, not_, null, func, text,exists
from sqlalchemy import desc

import random,time
from datetime import datetime

from services import GameService
from message.base import *
from message.resultdef import *

from db.connect import *

from proto.access_pb2 import *
from proto.game_pb2 import *
from proto.constant_pb2 import *
from proto.struct_pb2 import *


from util.handlerutil import *

from config.var import *

class RoomService(GameService):
    def init(self):
        self.registe_command(EnterGameServerReq,EnterGameServerResp,self.handle_enter_game_server)
        self.registe_command(QuitGameServerReq,QuitGameServerResp,self.handle_quit_game_server)
        self.registe_command(GetServerTimeReq,GetServerTimeResp,self.handle_get_server_time)
        self.registe_command(SitTableReq,SitTableResp,self.handle_sit_table)
        
        self.redis = self.server.redis
        
    def start_online(self,session,userid,event):
        self.notify_online(session,userid,event)

    def end_online(self,session,userid,event):
        self.notify_offline(session,userid)
    
    def notify_online(self,session,userid,event):
        req = create_client_message(OnlineReq)
        req.header.user = userid
        req.body.userid = userid
        req.body.access_service_id = event.srcId
        gevent.spawn_later(0.1,self.broadcast_message,req.header,req.encode())
        # self.broadcast_message(req.header,req.encode())
        
    def notify_offline(self,session,userid):
        req = create_client_message(OfflineReq)
        req.header.user = userid
        req.body.userid = userid
        gevent.spawn_later(0.1,self.broadcast_message,req.header,req.encode())
        #self.broadcast_message(req.header,req.encode())
    
    @USE_TRANSACTION
    def handle_enter_game_server(self,session,req,resp,event):        
        logging.info("====> User Connect Now: %d", req.header.user)
    
    @USE_TRANSACTION
    def handle_get_server_time(self,session,req,resp,event):        
        resp.body.server_time = int(time.time() * 1000)
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_quit_game_server(self,session,req,resp,event):
        logging.info("----> User Quit Now: %d", req.header.user)
        
        return False    
    
    @USE_TRANSACTION
    def handle_sit_table(self,session,req,resp,event):
        logging.info("----> User Sit Table: %d,so forward to game service", req.header.user)
        
        waitings = self.redis.hgetall("waitings")
        if len(waitings) == 0:
            req.header.result = -1
            return
        
        waiting_counts = [int(i) for i in waitings.values()]
        max_waiting = max(waiting_counts)
        
        for k,v in waitings.items():
            if int(v) == max_waiting:
                service_id = int(k)
        
        new_req = create_client_message(SitTable2Req)
        new_req.header.user = userid
        new_req.header.transaction = req.header.transaction
        new_req.body.type = req.body.type
        new_req.body.access_service_id = event.srcId
        self.forward_message_directly(service_id,new_req.header.command,req.header.user,req.header.transaction,new_req.encode())
        
        return False    
    
    
    
if __name__ == "__main__":
    pass

