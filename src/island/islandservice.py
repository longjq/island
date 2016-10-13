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
    
    def setup_route(self):
        self.registe_command(JoinGameReq,JoinGameResp,self.handle_join_game)
        self.registe_command(QueryGameWorldReq,QueryGameWorldResp,self.handle_query_world)
        self.registe_command(QueryGameStateReq,QueryGameStateResp,self.handle_query_state)
        self.registe_command(CreateForceReq,CreateForceResp,self.handle_create_force)
        self.registe_command(OfflineReq,OfflineResp,self.handle_user_offline)
    
    def init(self):
        self.user_sessions = {}
        self.manager = IslandGameManager(self)
    
    def get_user_info(self,session,user):
        account = session.query(TAccount).filter(TAccount.id == user).first()
        return account
    # 加入游戏
    @USE_TRANSACTION
    def handle_join_game(self,session,req,resp,event):
        # 获取用户信息
        user_info = self.get_user_info(session,req.header.user)
        power = 30
        # 用户ID, 事件源id?, 用户昵称, 请求游戏类型, 地图ID, 房间号, 游戏队伍, 命令实例
        game = self.manager.join_game(user_info.id,event.srcId,user_info.nick,req.body.game_type,req.body.map_id, \
                req.body.code,req.body.team,power,Commander(1,"sSSS"))
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

        for player in game.players.values():
            pb_player = resp.body.players.add()
            player.get_proto_struct(pb_player)

        resp.body.server_time = int(time.time() * 1000)
        resp.header.result = 0    

    # 创建军队
    @USE_TRANSACTION
    def handle_create_force(self,session,req,resp,event):
        user_info = self.get_user_info(session,req.header.user)
        game = self.manager.find_game(req.body.game_id)

        # 验证当前游戏数据是否存在、游戏是否准备完毕、用户是否在当前游戏中
        if game == None or not game.is_ready() or not game.has_player(req.header.user):
            resp.header.result = -1
            return
        # 在游戏数据中创建军队数据
        # 用户数据, 出生岛, 目标岛, 军力数据, 移动类型
        # todo...
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

    # 用户掉线
    @USE_TRANSACTION
    def handle_user_offline(self,session,req,resp,event):        
        self.manager.handle_user_offline(req.header.user)
        return False
    
if __name__ == "__main__":
    pass

