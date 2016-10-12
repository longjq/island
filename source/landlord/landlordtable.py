#coding: utf-8

import json
import logging
import traceback
from sqlalchemy.sql import select, update, delete, insert, and_,or_, subquery, not_, null, func, text,exists
from sqlalchemy import desc

import random,time

from collections import Counter
from datetime import datetime
from datetime import date as dt_date
from datetime import time as dt_time

from message.base import *
from message.resultdef import *


class Player:
    def __init__(self,user,access_service):
        self.user = user
        self.access_service = access_service
    

class Table:
    def __init__(self,manager,table_id,type):
        self.table_id = table_id
        self.in_game = False
        self.type = type
        self.manager = manager
        self.players = []
    
        
    def add_player(self,user,access_service):
        self.players.append(Player(user,access_service))
    
    def remove_player(self,user):
        for player in self.players:
            if player.user == user:
                self.players.remove(player)
                break
     
        return len(self.players) == 0 
     
    def dismiss(self):
        pass    
            
    def is_full(self):
        return len(self.players == 3)
        
        
    def notify_event(self,event):
        event_type = event.header.command
        event_data = event.encode()
        service = self.manager.service
        for player in self.players:
            service.send_client_event(player.access_service,player.user,event_type,event_data)    
        
        
class LandlordTableManager:
    def __init__(self,service):
        self.service = service
        self.redis = service.redis
        self.tables = {}
        self.waitings = []
        self.table_id = 0
    
    def new_table_id(self):
        self.table_id += 1
        return "%d-%d" % (self.serviceId,self.table_id)
        
    def sit_table(self,user,type,access_service):
        wait_list = [w for w in self.waitings if w.type == type]
        
        if len(wait_list) == 0:
            table_id = self.new_table_id()
            table = Table(self,table_id,type)
            table.add_player(user,access_service)
            self.waitings.append(table)
        else:
            waiting = wait_list[0]
            waiting.add_player(user,access_service)
            
            if waiting.is_full():
                self.waitings.pop()
                self.tables[waiting.table_id] = waiting
            table = waiting       
        
        self.redis.hset("waitings",self.serviceId,len(waitings)) 
        return table          
    
    def leave_table(self,user,table_id):
        for table in waitings:
            if table_id == table.table_id:
                need_dismiss = table.remove_player(player)
                if need_dismiss:
                    table.dismiss()
                break
                
        table = self.tables.get(table_id,None)
        if table != None:
            if table.in_game:
                return -1
            else:    
                table.remove_player(player)
                del self.tables[table_id]
                self.waitings.insert(0,table)
                
        self.redis.hset("waitings",self.serviceId,len(waitings)) 
        return 0
        
        
if __name__ == '__main__':
    pass
