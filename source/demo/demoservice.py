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


from util.handlerutil import *
from util.commonutil import *


class DemoService(GameService):
    def init(self):
        self.registe_command(FooReq,FooResp,self.handle_foo)
        self.users = {}

    @USE_TRANSACTION
    def handle_foo(self,session,req,resp,event):
        logging.info(">>>>>>>>>>>>>handle_foo comming>>>>>>>>>>>>>>>> %d",req.header.user)
        logging.info("############sssssssssssss###########")
        
        # create==================
        # hello_model = THello()
        # hello_model.title = req.body.title
        # hello_model.cate = req.body.cate
        # hello_model.desc = req.body.desc
        # session.add(hello_model)
        # print session.commit()

        # select==================
        # hello_model = session.query(THello).filter(THello.id==9).first()
        # if hello_model!= None:
        #     resp.body.message = str(hello_model.id)

        # delete==================
        # delete_result = session.query(THello).filter(THello.id==6).delete()
        # resp.body.message = str(delete_result)

        # update==================
        # update_result = session.query(THello).filter(THello.id==7).update({THello.title:'new title',THello.cate:33,THello.desc:'en,is ok'})
        # resp.body.message = str(update_result)
        

        resp.body.message += "|hell world|" + req.body.title
        logging.info("############sssssssssssss###########")
        self.users[req.header.user] = event.srcId

        gevent.spawn_later(2, self.call_all)

    def call_all(self):
        event = create_client_event(FooReq)
        event.body.title = "hello llllllllllllll"
        for uid,access_id in self.users.items():
            self.send_client_event(access_id,uid,event.header.command,event.encode())



    # @USE_TRANSACTION
    # def handle_test(self, session, req, resp, event):
        
    #     logging.info("<<<<<<<<<<test<<<<<<<<<<<<<<< %s", req.header.user)

    #     return False
    @USE_TRANSACTION
    def handle_bar(self,session,req,resp,event):
        logging.info(">>>>>>>>>>>>>handle_bar comming>>>>>>>>>>>>>>>> %d",req.header.user)
        # resp.body.message = " 22 hello " + req.body.name