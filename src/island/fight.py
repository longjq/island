#coding: utf-8
import gevent
from gevent import monkey;monkey.patch_all()
import json
import logging
import traceback

import binascii
from ctypes import *
from sqlalchemy.sql import select, update, delete, insert, and_, subquery, not_, null, func, text,exists
from sqlalchemy import desc

import math,random,time
from datetime import datetime
from threading import Lock

from db.connect import *


from config.var import *

from message.base import *

from proto.game_pb2 import *
from proto.constant_pb2 import *
from proto.access_pb2 import *
from proto import struct_pb2 as pb2

from islandgame import *

class FightVar:
    A = 0.18
    B = 0.96
    C = 1.04

    
FORCE_ATTRS = {
               USA:{"min_ap":12000,"max_ap":14000,"min_dp":12000,"max_dp":14000,"min_speed":800,"max_speed":1000},
               RUSSIA:{"min_ap":9000,"max_ap":16000,"min_dp":9000,"max_dp":16000,"min_speed":200,"max_speed":1600},
    }    
    
class Fighter:
    def __init__(self,id,force,troops):
        self.id = id
        self.force = force
        self.troops = troops
        self.hp = 10000 * troops / 5.0
        self.full_hp = 10000
        self.min_ap = self.get_force_attr(force,"min_ap")
        self.max_ap = self.get_force_attr(force,"max_ap")
        self.min_dp = self.get_force_attr(force,"min_dp")
        self.max_dp = self.get_force_attr(force,"max_dp")
        self.min_speed = self.get_force_attr(force,"min_speed")
        self.max_speed = self.get_force_attr(force,"max_speed")
        self.morale = force.morale
    
    def can_fight(self):
        return self.hp > 0 and self.morale > 0
        
    def is_dead(self):
        return self.hp <= 0        
        
    def get_force_attr(self,force,attr):
        return FORCE_ATTRS.get(force.force_type).get(attr)
        
    def get_speed(self):
        return random.randint(self.min_speed,self.max_speed) * self.morale
    
    def attack(self,fighter):
        ap = random.randint(self.min_ap,self.max_ap) * self.hp * 1.0  / self.full_hp
        dp = random.randint(fighter.min_dp,fighter.max_dp)  * fighter.hp * 1.0 / fighter.full_hp
        rate = random.randint(100 - int(fighter.morale),100 + int(self.morale)) * 1.0 / (fighter.morale + self.morale)
        
        damage = int(ap * (FightVar.C - 1/(FightVar.A * ap / dp + FightVar.B)) * rate)
        if damage < 0:
            damage = 0
        #print ap,dp,rate,damage
        fighter.hp -= damage
        if fighter.hp < 0 :
            fighter.hp = 0
        if rate >= 1.5:
            self.morale += self.morale * (rate - 1.5)
            fighter.morale -= fighter.morale * (rate - 1.4)
        elif rate >= 1.0:
            fighter.morale -= fighter.morale * 0.1
        elif rate <= 0.5:
            self.morale -= self.morale * (1-rate)
            fighter.morale += fighter.morale * 0.1
        elif rate < 1.0:        
            self.morale -= self.morale * 0.1
        
        self.morale = int(self.morale)
        fighter.morale = int(fighter.morale)
        self.morale = 10 if self.morale < 10 else self.morale
        self.morale = 100 if self.morale > 100 else self.morale
        fighter.morale = 10 if fighter.morale < 10 else fighter.morale
        fighter.morale = 100 if fighter.morale > 100 else fighter.morale

class Fight:
    def __init__(self):
        self.fighter_id = 0
        
    def get_fighter_id(self):
        self.fighter_id += 1
        return self.fighter_id    
    
    def get_fighters(self,force):
        troops = force.troops
        fighters = []
        while troops > 0:
            if troops >= 5:
                fighters.append(Fighter(self.get_fighter_id(),force,5))
                troops -= 5
            else:    
                fighters.append(Fighter(self.get_fighter_id(),force,troops))
                troops = 0
        return fighters
            
    def fight(self,force1,force2):
        fighters1 = self.get_fighters(force1)
        fighters2 = self.get_fighters(force2)
        
        rounds = 5
        for i in range(rounds):
            if len(fighters1) == 0 or len(fighters2) == 0:
                break
            self.fight_round(force1,force2,fighters1,fighters2)
        
        troops = 0
        morale = 0
        for fighter in fighters1:
            f_troops = int(fighter.hp * 5 / 10000)
            f_troops += 1 if fighter.hp * 5 % 10000 > 4000 else 0
            troops += f_troops
            morale += f_troops * fighter.morale
        force1.troops = troops
        force1.morale = morale / troops if troops != 0 else 10
        
        troops = 0
        morale = 0
        for fighter in fighters2:
            f_troops = int(fighter.hp * 5 / 10000)
            f_troops += 1 if fighter.hp * 5 % 10000 > 4000 else 0
            troops += f_troops
            morale += f_troops * fighter.morale
        force2.troops = troops
        force2.morale = morale / troops if troops != 0 else 10
        
        force1.morale = 10 if force1.morale < 10 else force1.morale
        force1.morale = 100 if force1.morale > 100 else force1.morale
        force2.morale = 10 if force2.morale < 10 else force2.morale
        force2.morale = 100 if force2.morale > 100 else force2.morale
        
        return
        
    def fight_round(self,force1,force2,fighters1,fighters2):
        sorted_fighters = fighters1 + fighters2 
        sorted_fighters.sort(cmp = lambda x,y: cmp(x.get_speed(),y.get_speed()))
        for fighter in sorted_fighters:
            if len(fighters2) == 0 or len(fighters1) == 0:
                break
            if not fighter.can_fight():
                continue
            if fighter in fighters1:
                target = random.choice(fighters2)
                fighter.attack(target)
                if target.is_dead():
                    fighters2.remove(target)
            else:
                target = random.choice(fighters1)
                fighter.attack(target)
                if target.is_dead():
                    fighters1.remove(target)
            
        
if __name__ == "__main__":
    fight = Fight()
    #def __init__(self,island_type,x,y,max_troops):
    #def __init__(self,force_type,uid,x,y,troops,morale,move_type,src,dst):
    s = Island(NORMAL,1,1,100)    
    d = Island(NORMAL,100,100,100)    
    
    force1 = Force(USA,1,1,1,150,110.90,STAY,s,d)
    force2 = Force(USA,1,1,1,150,110.90,STAY,s,d)
    
    fight.fight(force1,force2)
    
    print "--- force1 :",force1.troops,force1.morale
    print "--- force2 :",force2.troops,force2.morale