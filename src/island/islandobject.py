#coding: utf-8

import json
import logging
import traceback

import binascii
from ctypes import *
from sqlalchemy.sql import select, update, delete, insert, and_, subquery, not_, null, func, text,exists
from sqlalchemy import desc

import random,time,math
from datetime import datetime
from threading import Lock

from proto.game_pb2 import *
from proto.constant_pb2 import *
from proto.access_pb2 import *
from proto import struct_pb2 as pb2

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
        

class LinePoint:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        
class FlightLine:
    def __init__(self,id,src_island,dst_island,points):
        self.id = id
        self.src_island = src_island
        self.dst_island = dst_island        
        
        self.points = []
        self.points.insert(0,LinePoint(src_island.x,src_island.y))
        self.points.extend(points)
        self.points.append(LinePoint(dst_island.x,dst_island.y))
        
        self.directions = []
        
        for i,point in enumerate(self.points):
            if i == len(self.points) - 1:
                continue
            
            sx = point.x
            sy = point.y
            dx = self.points[i+1].x
            dy = self.points[i+1].y
            
            distance = self.get_distance(sx,sy,dx,dy) 
            w = dx - sx
            h = dy - sy
            self.directions.append((w/distance,h/distance,))            
    
    def get_line_point(self,line_seg):
        return self.points[line_seg],self.points[line_seg+1]        
    
    def get_distance(self,sx,sy,dx,dy):
        w = sx - dx
        h = sy - dy
        return math.sqrt(w * w + h * h) 
        
    def get_next_pos(self,src_island,dst_island,line_segment,x,y,distance):
        total_lines = len(self.points) - 1
        if line_segment > total_lines - 1:
            return total_lines - 1, dst_island.x, dst_island.y
        
        if src_island.id == self.src_island.id:
            src_point,dst_point = self.get_line_point(line_segment)
            direction_x,direction_y = self.directions[line_segment]
            distance_line_end = self.get_distance(x,y,dst_point.x,dst_point.y)
            #print src_point.x,src_point.y,dst_point.x,dst_point.y,direction_x,direction_y,distance_line_end
            if distance_line_end >= distance:
                return line_segment, x + distance * direction_x, y + distance * direction_y
            return self.get_next_pos(src_island,dst_island,line_segment + 1,dst_point.x,dst_point.y,distance - distance_line_end)
        else:   
            new_line_segment = total_lines - line_segment - 1
            dst_point,src_point = self.get_line_point(new_line_segment)
            direction_x,direction_y = self.directions[new_line_segment]
            direction_x = 0 - direction_x
            direction_y = 0 - direction_y
            
            distance_line_end = self.get_distance(x,y,dst_point.x,dst_point.y)
            #print src_point.x,src_point.y,dst_point.x,dst_point.y,direction_x,direction_y,distance_line_end
            if distance_line_end >= distance:
                return line_segment , x + distance * direction_x, y + distance * direction_y
            return self.get_next_pos(src_island,dst_island,line_segment + 1,dst_point.x,dst_point.y,distance - distance_line_end)    
        
    def get_proto_struct(self,line = None):
        if line == None:
            line = pb2.FlightLine()
        
        line.id = self.id
        line.src_island = self.src_island.id
        line.dst_island = self.dst_island.id
        
        for i,point in enumerate(self.points):
            if i == 0 or i == len(self.points) - 1:
                continue
            pb_point = line.points.add()
            pb_point.x = point.x
            pb_point.y = point.y        
    


class Island(CircleGameObject):
    def __init__(self,id,island_type,x,y,radius,max_troops,gun_radius = None,gun_life = None):  
        self.island_type = island_type
        self.x = x
        self.y = y
        self.max_troops = max_troops
        if radius <= 0:
            self.radius = Island.troops_to_radius(self.max_troops)
        else:
            self.radius = radius
                
        self.gun_radius = gun_radius
        self.gun_life = gun_life
        self.last_attack = time.time()
        self.lines = {}
            
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
        island.gun_radius = self.gun_radius
        island.gun_life = self.gun_life
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
        self.line_segment = 0
        self.src_island = src
        self.dst_island = dst
        self.set_troops(troops)
        self.create_time = int(time.time() * 1000)
        self.set_speed()
        self.is_removed = False

        if self.force_type == F_MISSILE and self.move_type == MOVE:
            distance = math.sqrt((dst.x - src.x) * (dst.x - src.x) + (dst.y - src.y) * (dst.y - src.y))
            self.direction_x = (dst.x - src.x) / distance
            self.direction_y = (dst.y - src.y) / distance
        
        
    def get_troops(self):
        return self.troops
    
    def set_troops(self,troops):
        self.troops = troops
        if self.move_type == STAY:
            self.radius = self.src_island.radius
        else:
            self.radius = 25
            #self.radius = math.sqrt(self.troops) * 3.5
            #if self.radius < 18:
            #    self.radius = 18
    
    def dec_troops(self,troops,world = None):
        self.troops -= troops
        if self.troops < 1:
            self.troops = 0
        if self.troops == 0 and world != None:
            world.remove_force(self.id)

    def set_speed(self):
        if self.force_type == F_NORMAL:
            self.speed = 30
        elif self.force_type == F_MISSILE:
            self.speed = 50
        
    def go_back(self):
        if self.move_type == STAY:
            return 
        self.move_type = MOVE
        self.src_island,self.dst_island = self.dst_island,self.src_island
        self.line_segment = 0
        self.set_speed()
        
            
    def get_radius(self):
        return self.radius    
        
    def is_reachs_destination(self):
        #print "---->",self.x,self.y,self.dst_island.x,self.dst_island.y
        return abs(self.x - self.src_island.x) >= abs(self.dst_island.x - self.src_island.x)  \
                and abs(self.y - self.src_island.y) >= abs(self.dst_island.y - self.src_island.y)

        #distance = self.distance_to_point(self.dst_island.x,self.dst_island.y)
        #return distance <= self.radius:
            
        #reached = self.dst_island.is_intersects_circle(self.x,self.y,self.radius)
        #if reached:
        #    print "dst_island",self.dst_island.x,self.dst_island.y,self.dst_island.radius,"self",self.x,self.y,self.radius
        #return reached

    # 静止时处理
    def stay(self,island,duration):
        if self.uid < 0:
            return 
        int_troops = int(self.troops)
            
        if self.move_type == STAY:
            if island.island_type == B_BORN :
                if int_troops > island.max_troops:
                    self.set_troops(self.troops - duration * 1)
                elif int_troops < island.max_troops:
                    rate = 1/ (1.0/1255.0 * (int_troops - 35) * (int_troops - 35) + 0.8)
                    addition = rate * duration
                   
                    troops = island.max_troops if (self.troops + addition) > island.max_troops else self.troops + addition
                    self.set_troops(troops)
            
            elif island.island_type == B_NORMAL or island.island_type == B_FORT:
                if int_troops > island.max_troops:
                    self.set_troops(self.troops - duration * 1)
                elif int_troops < island.max_troops:
                    if island.max_troops == 30:
                        rate = 1/ (13.0/1000.0 * (int_troops - 10) * (int_troops - 10) + 1.2)
                    elif island.max_troops == 60:   
                        rate = 1/ (11/4000 * (int_troops - 20) * (int_troops - 20) + 0.9)
                    else:
                        rate = 1/ (1.0/1000.0 * (int_troops - 30) * (int_troops - 30) + 0.6)
                    
                    addition = rate * duration
                    
                    troops = island.max_troops if (self.troops + addition) > island.max_troops else self.troops + addition
                    self.set_troops(troops)
                    
            elif island.island_type == B_MISSILE:
                rate =  0.1
                addition = rate * duration
                troops = island.max_troops if (self.troops + addition) > island.max_troops else self.troops + addition
                self.set_troops(troops)
                
            """
            if self.morale < 100:  
                old_morale = self.morale  
                if island.island_type == B_NORMAL:    
                    self.morale += duration * 15 * island.max_troops / 100.0
                else:
                    self.morale += duration * 30 * island.max_troops / 100.0               
                self.morale = 100 if self.morale > 100 else self.morale
                
                #print "---->",self.id,self.morale,self.morale - old_morale
            if self.troops - old_troops  != 0 or self.morale != 100:
                print "- stay ->",self,self.troops - old_troops,addition,self.morale,self.src_island.max_troops
            """
            
    def move(self,duration):
        if self.move_type == STAY:
            return
        #print "----->",self.id,self.x,self.y,self.dst_island.id,self.dst_island.x,self.dst_island.y    
        #self.x += duration * self.direction_x * self.speed 
        #self.y += duration * self.direction_y * self.speed
        if self.force_type == F_NORMAL:
            distance = duration * self.speed
            line = self.src_island.lines.get(self.dst_island.id)
            self.line_segment,self.x,self.y = line.get_next_pos(self.src_island,self.dst_island,self.line_segment,self.x,self.y,distance)
        elif self.force_type == F_MISSILE:
            distance = duration * self.speed
            self.x += distance * self.direction_x
            self.y += distance * self.direction_y
            

        """
        self.morale -=  duration * 2
        self.morale = 10 if self.morale < 10 else self.morale
        self.morale = 100
        """
    
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
        force.line_segment = self.line_segment
        force.is_removed = self.is_removed
        return force

    


class Commander:
    def __init__(self,id,name,properties = None):
        self.id = id
        self.name = name
        if properties != None:
            self.properties = properties
        else:
            self.properties = {}
        
    def get_rate(self,key):
        return self.properties.get(key,0)
    
    def get_proto_struct(self,commander = None):
        if commander == None:
            commander = pb2.Commander()
        
        commander.cid = self.id
        commander.name = self.name
        
        for k,v in self.properties.items():
            pb_property = commander.properties.add()
            pb_property.key = k
            pb_property.value = str(v)
                    

class World:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.islands = {}
        self.forces = {}  
        self.flight_lines = [] 
    
    def get_island(self,island_id):
        return self.islands.get(island_id)
    
    def add_island(self,island):
        self.islands[island.id] = island 

    def add_islands(self,islands):
        for island in islands:
            self.islands[island.id] = island
    
    def add_forces(self,forces):
        for force in forces:
            self.forces[force.id] = force 
            
    def add_force(self,force):
        self.forces[force.id] = force
     
    def remove_force(self,force_id):
        force = self.forces.pop(force_id)
        if force != None:
            force.is_removed = True
    
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

        for line in self.flight_lines:
            pb_line = world.lines.add()
            line.get_proto_struct(pb_line)       
        return world
    
class Player:
    def __init__(self,uid,access_id,name,team,color,power,commander):
        self.uid = uid
        self.access_id = access_id
        self.team = team
        self.name = name
        self.color = color
        self.is_online = True
        self.power = power
        self.commander = commander
    
    def __str__(self):
        return "uid=" + str(self.uid) + " name=" + self.name
        
    def get_proto_struct(self,player = None):
        if player == None:
            player = pb2.Player()
        player.uid = self.uid
        player.name = self.name
        player.team = self.team
        player.color = self.color
        player.is_online = self.is_online # TBD:
        player.power = int(self.power)
        self.commander.get_proto_struct(player.commander )
        return player



    
if __name__ == "__main__":
    pass

