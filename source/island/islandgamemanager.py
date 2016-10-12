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

from message.base import *

from db.connect import *
from config.var import *

from islandgame import *
from proto.constant_pb2 import *


class IslandGameManager:
    def __init__(self,service):
        self.games = {}
        self.code_games = {}
        self.service = service
        
    def notify_game_players(self,event,game,uid = None):    
        self.notify_some(event,*game.players.values())
        
    def notify_one(self,event,player):
        if player.uid >= 0:
            self.service.send_client_event(player.access_id,player.uid,event.header.command,event.encode())
        
    def notify_some(self,event,*players):
        event_data = event.encode()
        for player in players:
            if player.uid >= 0:
                self.service.send_client_event(player.access_id,player.uid,event.header.command,event_data)
        
    def new_game(self,game_type,code):
        game = IslandGame(self,game_type,code)
        if code != None:
            self.code_games[code] = game
        self.games[game.id] = game
        return game    
        
    def leave_game(self,uid):
        game = self.find_game_by_uid(uid)    
        if game != None:
            self.remove_game(game.id)
        
    def join_game(self,uid,access_id,name,game_type,code,team,force_type,power):
        if code == None or len(code) < 4:
            code = None
        
        game = None
        if code != None:
            game = self.code_games.get(code)
            if game == None:
                game = self.new_game(game_type,code)
        else:
            for k,g in self.games.items():
                if g.has_player(uid) and not g.has_code():
                    game = g
                    break
                    
            if game == None:        
                not_ready = None
                for k,g in self.games.items():
                    if not g.is_ready():
                        not_ready = g
                        break
                if not_ready == None:            
                    game = self.new_game(game_type,None)
                else:
                    game = not_ready
                    
        if game.add_player(uid,access_id,name,team,force_type,power) < 0:
            return None
        
        event = create_client_event(GameStateEvent)
        game.set_proto_game_state(event.body.game)
        event.body.ready = game.is_ready()
        
        self.notify_game_players(event,game)
        return game    
        
    def handle_user_offline(self,uid):
        game = self.find_game_by_uid(uid)
        if game == None:
        	return 
        if not game.is_ready():
            self.remove_game(game.id)
        else:
            game.players[uid].is_online = False
            uids = game.get_player_uids(None)
            has_one = False
            for uid in uids:
                if self.service.server.redis.hget("online",uid):
                    has_one = True
                    break
            if not has_one :
                self.remove_game(game.id)
            else:
                event = create_client_event(GameStateEvent)
                game.set_proto_game_state(event.body.game)
                event.body.ready = game.is_ready()
        
                self.notify_game_players(event,game)
        
    def find_game_by_uid(self,uid):
        for k,v in self.games.items():
            if v.has_player(uid):
                return v
        return None    
        
    def find_game(self,id):
        return self.games.get(id)        
        
    def remove_game(self,game_id):
        game = self.games.pop(game_id,None)
        if game != None:
            self.code_games.pop(game.code,None)                
            if game.is_ready():
                game.game_over()
        print "------> game is over ----->",game_id        
        
    def remove_game_since_over(self,game_id):
        game = self.games.pop(game_id,None)
        if game != None:
            self.code_games.pop(game.code,None)        
            

