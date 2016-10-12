#coding: utf-8

import json
import logging
import traceback

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
from db.account import *

from proto.access_pb2 import *
from proto.constant_pb2 import *
from proto.struct_pb2 import *

from util.handlerutil import *

from islandgamemanager import *

from config.var import *

class IslandService(GameService):
    def init(self):
        self.user_sessions = {}
        
        self.registe_command(JoinGameReq,JoinGameResp,self.handle_join_game)
        self.registe_command(QueryGameWorldReq,QueryGameWorldResp,self.handle_query_world)
        self.registe_command(QueryGameStateReq,QueryGameStateResp,self.handle_query_state)
        self.registe_command(CreateForceReq,CreateForceResp,self.handle_create_force)
        self.registe_command(OfflineReq,OfflineResp,self.handle_user_offline)
        
        self.manager = IslandGameManager(self)
        
    
    def get_user_info(self,session,user):
        account = session.query(TAccount).filter(TAccount.id == user).first()
        return account
    
    @USE_TRANSACTION
    def handle_join_game(self,session,req,resp,event):        
        user_info = self.get_user_info(session,req.header.user)
        power = 10
        game = self.manager.join_game(user_info.id,event.srcId,user_info.nick,
        	req.body.game_type,req.body.code,req.body.team,req.body.force_type,power)
        if game == None:
            resp.header.result = -1
            return 
        resp.body.game_id = game.id
        resp.body.ready = game.is_ready()
        resp.header.result = 0
        
    @USE_TRANSACTION
    def handle_query_world(self,session,req,resp,event):
        user_info = self.get_user_info(session,req.header.user)
        
        game = self.manager.find_game(req.body.game_id)
        
        if game == None or not game.is_ready():
            resp.header.result = -1
            return
        game.world.get_proto_struct(resp.body.world)
        resp.body.server_time = int(time.time() * 1000)
        resp.header.result = 0    
    
    @USE_TRANSACTION
    def handle_create_force(self,session,req,resp,event):
        user_info = self.get_user_info(session,req.header.user)
        game = self.manager.find_game(req.body.game_id)
        
        if game == None or not game.is_ready() or not game.has_player(req.header.user):
            resp.header.result = -1
            return
        
        force = game.create_force(req.header.user,req.body.src_island,req.body.dst_island,req.body.troops,req.body.move_type)
        if force == None:
            resp.header.result = -1
            return
        resp.header.result = 0
    
    @USE_TRANSACTION
    def handle_query_state(self,session,req,resp,event):
        game = self.manager.find_game(req.body.game_id)
        if game == None:
            resp.header.result = -1
            return
        
        game.set_proto_game_state(resp.body.state)
        resp.header.result = 0

    @USE_TRANSACTION
    def handle_user_offline(self,session,req,resp,event):        
        self.manager.handle_user_offline(req.header.user)
        return False
    
if __name__ == "__main__":
    pass

