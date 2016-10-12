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

from fight import *

class AutoIncrease:
    def __init__(self,value = None):
        self.lock = Lock()
        if value == None:
            value = 0
        self.value = value

    def get(self):
        self.lock.acquire()
        try :
            self.value += 1
            return self.value
        finally:
            self.lock.release()

game_id = AutoIncrease()
island_id = AutoIncrease()
force_id = AutoIncrease()        
        
        
class CircleGameObject:
    def distance_to_point(self,x,y):
        dx = self.x - x
        dy = self.y - y
        return math.sqrt(dx * dx + dy * dy)        
    
    def is_contains_point(self,x,y):
        return self.distance_to_point(x,y) <= self.radius
        
    def is_intersects_circle(self,x,y,radius):
        return self.distance_to_point(x,y) <= (self.radius + radius)
    
class Island(CircleGameObject):
    def __init__(self,island_type,x,y,max_troops):
        self.id = island_id.get()
        self.island_type = island_type
        self.x = x
        self.y = y
        self.max_troops = max_troops
        self.radius = Island.troops_to_radius(self.max_troops)
            
    @staticmethod
    def troops_to_radius(troops):
        return math.sqrt(troops) * 5.8
        
    def get_radius(self):
        return self.radius    
    
    def __repr__(self):
        return "id=%d,max_troops=%d,x=%d,y=%d,type=%d" % (self.id,self.max_troops,
                                                self.x,self.y,self.island_type)        
    
    def get_proto_struct(self,island = None):
        if island == None:
            island = pb2.Island()
        island.id = self.id
        island.island_type = self.island_type
        island.x = self.x
        island.y = self.y
        island.max_troops = self.max_troops
        island.radius = self.radius
        return island    
        
class Force(CircleGameObject):
    def __init__(self,force_type,uid,x,y,troops,morale,move_type,src,dst):
        self.id = force_id.get()
        self.force_type = force_type
        self.uid = uid
        self.x = x
        self.y = y
        
        self.morale = morale
        self.move_type = move_type
        self.src_island = src
        self.dst_island = dst
        self.set_troops(troops)
        self.create_time = int(time.time() * 1000)
        self.set_speed()
        self.set_direction()
    
    def get_troops(self):
        return self.troops
    
    def set_troops(self,troops):
        self.troops = troops
        if self.move_type == STAY:
            self.radius = self.src_island.radius
        else:
            self.radius = 20
            #self.radius = math.sqrt(self.troops) * 3.5
            #if self.radius < 18:
            #    self.radius = 18
        
    def set_direction(self):
        if self.move_type == STAY or self.src_island == self.dst_island:
            return 
        distance = self.dst_island.distance_to_point(self.x,self.y)
        self.direction_x = (self.dst_island.x - self.x) / distance
        self.direction_y = (self.dst_island.y - self.y) / distance
    
    def set_speed(self):
        if self.force_type == USA:
            self.speed = 30
        else:
            self.speed = 30
        
        
    def go_back(self):
        if self.move_type == STAY:
            return 
        self.move_type = MOVE
        self.src_island,self.dst_island = self.dst_island,self.src_island
        self.set_speed()
        self.set_direction()
    
    def get_radius(self):
        return self.radius    
        
    def is_reachs_destination(self):
        reached = self.dst_island.is_intersects_circle(self.x,self.y,self.radius)
        #if reached:
        #    print "dst_island",self.dst_island.x,self.dst_island.y,self.dst_island.radius,"self",self.x,self.y,self.radius
        return reached
        
    def stay(self,island,duration):
        if self.uid < 0:
            return 
            
        if self.move_type == STAY:
            if island.island_type == NORMAL :
                if self.troops >= island.max_troops:
                    return
                addition = island.max_troops * duration / 60
                old_troops = self.troops
                troops = island.max_troops if (self.troops + addition) > island.max_troops else self.troops + addition
                self.set_troops(troops)
                addition = self.troops - old_troops
            
            
            if self.morale < 100:  
                old_morale = self.morale  
                if island.island_type == NORMAL:    
                    self.morale += duration * 15 * island.max_troops / 100.0
                else:
                    self.morale += duration * 30 * island.max_troops / 100.0               
                self.morale = 100 if self.morale > 100 else self.morale
                
                #print "---->",self.id,self.morale,self.morale - old_morale
            #if self.troops - old_troops  != 0 or self.morale != 100:
            #    print "- stay ->",self,self.troops - old_troops,addition,self.morale,self.src_island.max_troops
        
            
    def move(self,duration):
        if self.move_type == STAY:
            return
        #print "----->",self.id,self.x,self.y,self.dst_island.id,self.dst_island.x,self.dst_island.y    
        self.x += duration * self.direction_x * self.speed 
        self.y += duration * self.direction_y * self.speed
        self.morale -=  duration * 2
        self.morale = 10 if self.morale < 10 else self.morale
        self.morale = 100
    
    def __repr__(self):
        return "id=%d,uid=%d,troops=%d,morale=%d,x=%d,y=%d,src=%d,dst=%d,force=%d" % (self.id,self.uid,self.troops,self.morale,
                     self.x,self.y,self.src_island.id,self.dst_island.id,self.force_type)    

    def get_proto_struct(self,force = None):
        if force == None:
            force = pb2.Force()
        force.id = self.id
        force.force_type = self.force_type
        force.uid = self.uid
        force.x = self.x
        force.y = self.y
        force.troops = self.troops
        force.morale = self.morale
        force.move_type = self.move_type
        force.src_island = self.src_island.id
        force.dst_island = self.dst_island.id
        force.create_time = self.create_time
        force.radius = self.radius 
        force.speed = self.speed
        return force
        
    def fight_with(self,force):
        #print "----> fight happen :",self,force
        #f = Fight()
        #f.fight(self,force)
        #print "----> fight result :",self,force
        # simple fight
        power = self.troops * self.morale
        other_power = force.troops * force.morale
        
        if power >= other_power:
            self.troops = (power - other_power) / self.morale if self.morale != 0 else 0
            force.troops = 0
        else:
            self.troops = 0 
            force.troops = (other_power - power) / force.morale if force.morale != 0 else 0
        
        

class World:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.islands = {}
        self.forces = {}   
    
    def get_island(self,island_id):
        return self.islands.get(island_id)
        
    def add_islands(self,islands):
        for island in islands:
            self.islands[island.id] = island
    
    def add_forces(self,forces):
        for force in forces:
            self.forces[force.id] = force 
            
    def add_force(self,force):
        self.forces[force.id] = force
     
    def remove_force(self,force_id):
        self.forces.pop(force_id)
    
    def get_island_stay_force(self,island_id):
        for k,force in self.forces.items():
            if force.move_type == STAY and force.src_island.id == island_id:
                return force
        return None
    
    def get_island_my_stay_force(self,uid,island_id):
        for k,force in self.forces.items():
            if force.uid == uid and force.move_type == STAY and force.src_island.id == island_id:
                return force
        return None
     
    def get_proto_struct(self,world = None):
        if world == None:
            world = pb2.GameWorld()
        world.width = self.width
        world.height = self.height
        
        for k,v in self.islands.items():
            pb_island = world.islands.add()
            v.get_proto_struct(pb_island)
            
        for k,v in self.forces.items():
            pb_force = world.forces.add()
            v.get_proto_struct(pb_force)    
        return world
    
class Player:
    def __init__(self,uid,access_id,name,team,force_type,color,power):
        self.uid = uid
        self.access_id = access_id
        self.team = team
        self.force_type = force_type
        self.name = name
        self.color = color
        self.is_online = True
        self.power = power
    
    def __str__(self):
        return "uid=" + str(uid) + " name=" + name
        
    def get_proto_struct(self,player = None):
        if player == None:
            player = pb2.Player()
        player.uid = self.uid
        player.force_type = self.force_type
        player.name = self.name
        player.team = self.team
        player.color = self.color
        player.is_online = self.is_online # TBD:
        player.power = self.power
        return player
        
class IslandGame:
    def __init__(self,manager,game_type,code):
        self.id = game_id.get()
        self.code = code
        self.game_type = game_type
        self.players = {}
        self.robot_player = Player(-1,-1,"lxk",100,USA if random.randint(1,10)>5 else RUSSIA,-1,2)
        self.world = None
        self.manager = manager
        self.sender = EventSender(self.manager,self)
        self.is_over = False
        
    def has_code(self):
        return self.code != None    
        
    def game_over(self):    
        self.is_over = True
        
    def test_ai(self):
        forces = self.world.forces.values()
        random.shuffle(forces)
        for force in forces:
            if force.uid > 0:
                dst_island = None
                targets = self.world.islands.values()
                random.shuffle(targets)
                for island in targets:
                    if force.src_island.id == island.id:
                        continue
                    dst_island = island
                    break
                self.create_force(force.uid,force.src_island.id,dst_island.id,force.troops/2,MOVE)
                break    
        
    def run(self):
        duration = 0.05
        begin = int(time.time())
        winner = -1
        
        while not self.is_over and (time.time() - begin) < 1200:
            forces = self.world.forces.values()
            random.shuffle(forces)
            for force in forces:
                if force.troops <= 0:
                    continue
                if force.move_type == STAY:
                    island = self.world.get_island(force.src_island.id)
                    force.stay(island,duration)
                else:
                    try :
                        force.move(duration)
                    except:
                        traceback.print_exc()
                        #print "[ERR]",force
                        continue
                    if force.is_reachs_destination():
                        #print "----> reach destination"
                        island_force = self.world.get_island_stay_force(force.dst_island.id)
                        # 0. 岛屿中没有部队
                        if island_force == None:
                            force.move_type = STAY
                            force.src_island = force.dst_island
                            force.x = force.dst_island.x 
                            force.y = force.dst_island.y
                            self.sender.update_force_event(self,force)
                        # 1. 同一个用户：合并
                        elif force.uid == island_force.uid:   
                            island_force.morale = (island_force.morale * island_force.troops + force.morale * force.troops) / (island_force.troops + force.troops)
                            troops = island_force.troops + force.troops
                            island_force.set_troops(troops)
                            self.world.remove_force(force.id)
                            self.sender.merge_force_event(self,island_force,force)
                        # 2. 不同用户，同一个组：部队返回    
                        elif self.get_player(force.uid).team == self.get_player(island_force.uid).team:
                            force.go_back()
                            self.sender.update_force_event(self,force)
                        
                        # 3. 不同用户，战斗
                        elif self.get_player(force.uid).team != self.get_player(island_force.uid).team:
                            #print "---> fight with island team"
                            force.fight_with(island_force)
                            if force.troops == 0:
                                self.world.remove_force(force.id)
                            if island_force.troops == 0:
                                self.world.remove_force(island_force.id)
                                
                            if force.troops != 0:
                                if island_force.troops == 0:
                                    force.move_type = STAY
                                    force.src_island = force.dst_island
                                    force.x = force.src_island.x
                                    force.y = force.src_island.y
                                else:
                                    force.go_back()
                                    
                            self.sender.fight_in_island_event(self,force,island_force)
                            
            
            forces = self.world.forces.values()
            #random.shuffle(forces)
            for k,force in enumerate(forces):
                if force.troops <= 0:
                    continue
                for j in range(k+1,len(forces)):
                    other_force = forces[j]
                    if other_force == None or other_force.troops <= 0 or force.troops <= 0:
                        continue
                        
                    if force.move_type == STAY or other_force.move_type == STAY:
                        continue    
                    if not other_force.is_intersects_circle(force.x,force.y,force.radius):
                        continue
                    # 1. 同一个用户,同一个目标：合并
                    if force.uid == other_force.uid and force.dst_island.id == other_force.dst_island.id:
                        #other_force.morale = (force.morale * force.troops + other_force.morale * other_force.troops) / (other_force.troops + force.troops)
                        #troops = other_force.troops + force.troops
                        #other_force.set_troops(troops)
                        #self.world.remove_force(force.id)
                        #self.sender.merge_force_event(self,other_force,force)
                        break
                    # 2. 不同用户，且不是同一个组: 战斗
                    elif self.get_player(force.uid).team != self.get_player(other_force.uid).team:
                        force.fight_with(other_force)
                        if force.troops == 0:
                            self.world.remove_force(force.id)
                        if other_force.troops == 0:
                            self.world.remove_force(other_force.id)
                            
                        if force.troops != 0:
                            if other_force.troops != 0:
                                force.go_back()
                                other_force.go_back()
                                
                        self.sender.fight_in_air_event(self,force,other_force)            
            #if random.randint(1,100) > 95:
            #    self.test_ai()    
            #    print "---create force now ->"
        
            forces = self.world.forces.values()
            has_two_team = False
            only_uid = -1
            for force in forces:
                if force.uid < 0:
                    continue
                if only_uid < 0:
                    only_uid = force.uid
                    continue
                if only_uid != force.uid:
                    has_two_team = True
                    break
            
            if only_uid < 0:
                winner = -1
                break
            elif not has_two_team:
                winner = only_uid
                break
            
            gevent.sleep(duration)
    
        if winner < 0:
            name = ""
        else:    
            player = self.get_player(winner)
            name = player.name
        self.sender.game_over_event(self,winner,name)            
        self.manager.remove_game_since_over(self.id)    
    
    

    def create_world(self):
        self.world = World(480,800)
        self.create_islands()
        gevent.spawn(self.run)
        
        
    def create_islands(self):
        if self.game_type == G2X2:
            players = self.players.values()
            random.shuffle(players)
            islands = self.create_some_islands_in_area(1,1,(30,),0,0,480,150)       
            forces = self.create_initial_forces(players[0],islands)
            self.world.add_islands(islands)
            self.world.add_forces(forces)
            islands = self.create_some_islands_in_area(1,1,(30,),0,650,480,150) 
            forces = self.create_initial_forces(players[1],islands)     
            self.world.add_islands(islands)
            self.world.add_forces(forces)
            
            other_islands = self.create_some_islands_in_area(8,12,(30,60,90,),0,160,480,480) 
            
            for island in other_islands:
                troops = int(island.max_troops * 0.8)
                force_type = USA if random.randint(1,10) > 5 else RUSSIA    
                force = Force(force_type,-1,island.x,island.y,troops,80,STAY,island,island)
                forces.append(force)
            
            self.world.add_islands(other_islands)
            
    def create_islands_random(self):
        MIN_TROOPS = 40
        MAX_TROOPS = 80
        if self.game_type == G2X2:
            MIN_COUNTOF = 5
            MAX_COUNTOF = 10
            players = self.players.values()
            random.shuffle(players)
            islands = self.create_islands_in_area(MIN_COUNTOF,MAX_COUNTOF,MIN_TROOPS,MAX_TROOPS,0,0,480,390)
            forces = self.create_initial_forces(players[0],islands)
            self.world.add_islands(islands)
            self.world.add_forces(forces)
            
            islands = self.create_islands_in_area(MIN_COUNTOF,MAX_COUNTOF,MIN_TROOPS,MAX_TROOPS,0,390,480,390)
            forces = self.create_initial_forces(players[1],islands)
            self.world.add_islands(islands)
            self.world.add_forces(forces)
            
        elif self.game_type == G4X4:
            MIN_COUNTOF = 5
            MAX_COUNTOF = 10
            players = self.players.values()
            random.shuffle(players)
            islands = self.create_islands_in_area(MIN_COUNTOF,MAX_COUNTOF,MIN_TROOPS,MAX_TROOPS,0,0,240,390)
            forces = self.create_initial_forces(players[0],islands)
            self.world.add_islands(islands)
            self.world.add_forces(forces)
            
            islands = self.create_islands_in_area(MIN_COUNTOF,MAX_COUNTOF,MIN_TROOPS,MAX_TROOPS,240,0,240,390)
            forces = self.create_initial_forces(players[1],islands)
            self.world.add_islands(islands)
            self.world.add_forces(forces)
            
            islands = self.create_islands_in_area(MIN_COUNTOF,MAX_COUNTOF,MIN_TROOPS,MAX_TROOPS,0,390,240,390)
            forces = self.create_initial_forces(players[2],islands)
            self.world.add_islands(islands)
            self.world.add_forces(forces)
            
            islands = self.create_islands_in_area(MIN_COUNTOF,MAX_COUNTOF,MIN_TROOPS,MAX_TROOPS,240,390,240,390)
            forces = self.create_initial_forces(players[3],islands)
            self.world.add_islands(islands)
            self.world.add_forces(forces)
    
    
    def create_some_islands_in_area(self,min_count,max_count,troops_choice,x,y,w,h):
        total = random.randint(min_count,max_count)
        islands = []
              
        for i in xrange(total):
            try_times = 0
            while try_times < 20:
                try_times += 1
                troops = random.choice(troops_choice)#random.randint(min_troops,max_troops)
                radius = Island.troops_to_radius(troops)
                ix = random.randint(int(x + radius),int(x + w - radius))
                iy = random.randint(int(y + radius),int(y + h - radius))
                is_intersects = False
                for island in islands:
                    if island.is_intersects_circle(ix,iy,radius):
                        is_intersects = True
                        break
                
                if not is_intersects :
                    #island_type = NORMAL if random.randint(1,10) > 3 else ONLY_REST
                    island_type = NORMAL
                    islands.append(Island(island_type,ix,iy,troops))
                    break
        
        return islands      
    
    def create_islands_in_area(self,min_count,max_count,min_troops,max_troops,x,y,w,h):
        total = random.randint(min_count,max_count)
        islands = []
              
        for i in xrange(total):
            try_times = 0
            while try_times < 20:
                try_times += 1
                troops = random.choice((30,60,90),)#random.randint(min_troops,max_troops)
                radius = Island.troops_to_radius(troops)
                ix = random.randint(int(x + radius),int(x + w - radius))
                iy = random.randint(int(y + radius),int(y + h - radius))
                is_intersects = False
                for island in islands:
                    if island.is_intersects_circle(ix,iy,radius):
                        is_intersects = True
                        break
                
                if not is_intersects :
                    #island_type = NORMAL if random.randint(1,10) > 3 else ONLY_REST
                    island_type = NORMAL
                    islands.append(Island(island_type,ix,iy,troops))
                    break
        
        return islands                    
        
    def create_initial_forces(self,player,islands):    
        MAX_TROOPS = 150
        total = 0
        random_islands = []
        random_islands.extend(islands)
        random.shuffle(random_islands)
        forces = []
        for island in random_islands:
            if total < MAX_TROOPS:
                troops = int(island.max_troops * 0.8)
                if troops + total > MAX_TROOPS:
                    troops = MAX_TROOPS - total
                force = Force(player.force_type,player.uid,island.x,island.y,troops,80,STAY,island,island)
                forces.append(force)
                total += troops
            else:
                troops = int(island.max_troops * 0.8)
                force_type = USA if random.randint(1,10) > 5 else RUSSIA    
                force = Force(force_type,-1,island.x,island.y,troops,30,STAY,island,island)
                forces.append(force)
        return forces        
        
    def create_force(self,uid,src_island_id,dst_island_id,troops,move_type):
        player = self.players.get(uid)
        if player == None:
            return None
        
        player_forces = [f for f in self.world.forces.values() if f.uid == uid and f.move_type != STAY]
        if len(player_forces) >= player.power:
            return None
        
        island_force = self.world.get_island_my_stay_force(uid,src_island_id)
        if island_force == None or island_force.troops < troops:
            return None
        src_island = self.world.get_island(src_island_id)    
        dst_island = self.world.get_island(dst_island_id)    
        force_type = self.players[uid].force_type
        force = Force(force_type,uid,island_force.x,island_force.y,troops,island_force.morale,move_type,src_island,dst_island)
        self.world.add_force(force)
        new_troops = island_force.troops - troops
        island_force.set_troops(new_troops)
        if island_force.troops == 0:
            self.world.remove_force(island_force.id)
            
        self.sender.new_force_event(self,force,island_force)        
        return force
        
    def has_player(self,uid):
        return uid in self.players        
        
    def add_player(self,uid,access_id,name,team,force_type,power):
        if uid in self.players:
            self.players[uid].is_online = True
            return uid
        
        if len(self.players) >= self.game_type * 2:
            return -1
        
        if int(team) in (1,2):
            countof = 0
            for player in self.players.values():
                if player.team == team:
                    countof += 1
            
            if countof >= self.game_type:
                return -1
                
        else:
            team1 = [player for player in self.players.values() if player.team == 1]
            team2 = [player for player in self.players.values() if player.team == 2]
            team = 1 if len(team1) < len(team2) else 2
        
        if force_type == UNKNOWN:
            force_type = USA if random.randint(1,10) > 5 else RUSSIA
                
        player = Player(uid,access_id,name,team,force_type,len(self.players),power)
        self.players[player.uid] = player
        
        if self.is_ready():
            self.create_world()
        return 0
        
    def remove_player(self,uid):
        if self.is_ready():
            return False
        self.players.pop(uid,None)                    
        
    def is_ready(self):
        return len(self.players) == (self.game_type * 2)
        
    def get_player(self,uid):
        if uid < 0:
            return self.robot_player
        return self.players.get(uid)
        
    def get_player_uids(self,except_one):
        uids = []
        for player in self.players.values():
            if player.uid >= 0 and player.uid != except_one:
                uids.append(player.uid)
        return uids    
        
        
    def set_proto_game_state(self,state):
        state.game_id = self.id
        for player in self.players.values():
            state.players._values.append(player.get_proto_struct())
        return state


class EventSender:
    def __init__(self,manager,game):
        self.manager = manager
        self.game = game
        
    def new_force_event(self,game,force,island_force):
        event = create_client_event(NewForceEvent)
        force.get_proto_struct(event.body.new_force)
        island_force.get_proto_struct(event.body.island_force)
        event.body.server_time = int(time.time() * 1000)
        event.body.game_id = game.id
        if self.manager:
            self.manager.notify_game_players(event,self.game)        

    def update_force_event(self,game,force):
        event = create_client_event(UpdateForceEvent)
        force.get_proto_struct(event.body.force)
        event.body.server_time = int(time.time() * 1000)
        event.body.game_id = game.id
        if self.manager:
            self.manager.notify_game_players(event,self.game)        

    def merge_force_event(self,game,target_force,force):
        event = create_client_event(MergeForceEvent)
        target_force.get_proto_struct(event.body.target_force)
        force.get_proto_struct(event.body.force)
        event.body.server_time = int(time.time() * 1000)
        event.body.game_id = game.id
        if self.manager:
            self.manager.notify_game_players(event,self.game)        
    
    def fight_in_island_event(self,game,force,island_force):
        event = create_client_event(FightInIslandEvent)
        island_force.get_proto_struct(event.body.island_force)
        force.get_proto_struct(event.body.force)
        event.body.server_time = int(time.time() * 1000)
        event.body.game_id = game.id
        if self.manager:
            self.manager.notify_game_players(event,self.game)                
        
    def fight_in_air_event(self,game,force,other_force):
        event = create_client_event(FightInAirEvent)
        other_force.get_proto_struct(event.body.other_force)
        force.get_proto_struct(event.body.force)
        event.body.server_time = int(time.time() * 1000)
        event.body.game_id = game.id
        if self.manager:
            self.manager.notify_game_players(event,self.game)                
    
    def game_over_event(self,game,winner,name):
        event = create_client_event(GameOverEvent)
        
        event.body.server_time = int(time.time() * 1000)
        event.body.winner = winner
        event.body.name = name
        event.body.game_id = game.id
        if self.manager:
            self.manager.notify_game_players(event,self.game)                
    
        
if __name__ == "__main__":
    game = IslandGame(None,G4X4,"123")
    
    game.add_player(1,"lxk1",1,USA)
    game.add_player(2,"lxk2",1,USA)
    
    game.add_player(3,"lxk3",2,USA)
    game.add_player(4,"lxk4",2,RUSSIA)
    #import pprint    
    #pprint.pprint(game.world.islands)
    #pprint.pprint(game.world.forces)
    
    #print game.world.get_proto_struct()
    forces = game.world.forces.values()
    for force in forces:
        if force.uid == 1:
            dst_island = None
            for island in game.world.islands.values():
                dst_island = island
                break
            game.create_force(1,force.src_island.id,dst_island.id,force.troops/2,MOVE)
            break
    
    game.run()
    
    