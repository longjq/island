#coding: utf-8

import json
import logging
import traceback
import socket
import gevent
import binascii
from ctypes import *
from sqlalchemy.sql import select, update, delete, insert, and_,or_, subquery, not_, null, func, text,exists
from sqlalchemy import desc

import random,time
from datetime import datetime
from datetime import date as dt_date
from datetime import time as dt_time


from services import GameService
from message.base import *
from message.resultdef import *

from proto.constant_pb2 import *
from proto.access_pb2 import *
from proto.game_pb2 import *

from db.connect import *
from db.role import *


from util.handlerutil import *
from util.commonutil import *


class LandlordService(GameService):
    def init(self):
        self.registe_command(SitTable2Req,SitTableResp,self.handle_sit_table)
        self.registe_command(PlayLandlordReq,PlayLandlordResp,self.handle_play_landlord)
        self.registe_command(GetLandlordTableReq,GetLandlordTableResp,self.handle_get_landlord)
        self.registe_command(CallCardReq,CallCardResp,self.handle_call_card)
        self.registe_command(PlayCardReq,PlayCardResp,self.handle_play_card)
        
        self.redis = self.server.redis
        self.redis.hset("waitings",self.serviceId,0)
        
        self.table_manager = LandlordTableManager(self)
     
     
    @USE_TRANSACTION
    def handle_sit_table(self,session,req,resp,event):
        logging.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<< %d",req.header.user)
        
        resp.header.user = req.body.user
        resp.header.transaction = req.body.transaction
        
        table = self.table_manager.sit_table(req.body.user,req.body.type,req.body.access_service)
        if table == None:
            # No Table exist
            resp.header.result = -1
        else:
            # later,all message will be sent to this service
            resp.body.route = self.serviceId
            resp.body.table = table.table_id
            resp.header.result = 0
        
        self.forward_message_directly(req.body.access_service,resp.header.command,req.body.user,req.body.transaction,resp.encode())
        return False 
        
    @USE_TRANSACTION
    def handle_play_landlord(self,session,req,resp,event):
        logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> %d",req.header.user)
        access_server_id = self.server.redis.hget("mapping",req.header.user)
        #access_server_id = event.srcId
        event = create_client_event(GameEvent,req.header.user)
        event.body.name = "hello world"
        self.send_client_event(access_server_id,req.header.user,1,GameEvent.DEF.Value("ID"),event.encode())
        
        gevent.spawn_later(20,self.send_client_event,access_server_id,req.header.user,1,GameEvent.DEF.Value("ID"),event.encode())
        
        return False
    
    @USE_TRANSACTION
    def handle_offline(self,session,req,resp,event):
        logging.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<< %d",req.header.user)
        
        return False
        
    @USE_TRANSACTION
    def handle_call_card(self,session,req,resp,event):
        logging.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<< %d",req.header.user)
        
        return False
        
    @USE_TRANSACTION
    def handle_play_card(self,session,req,resp,event):
        logging.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<< %d",req.header.user)
        
        return False    