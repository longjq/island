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

from islandobject import *
from islandmap import *
  
class WorldCreator:
    def __init__(self):
        pass
    # 创建地图
    # 传入redis,地图id,游戏类型,游戏世界,玩家集合
    def create_by_map(self,r,map_id,game_type,world,players):
        if map_id < 0:
            map_id = get_any_map(r,game_type)
        setup_world(r,map_id,world,players)    
        return map_id

    def create_G1X1(self,world,players):
        players = players.values()
        random.shuffle(players)
        
        islands = self.create_islands_in_area(0,0,480,50,B_NORMAL,1,(30,),0,0)       
        forces = self.create_island_forces(30,players[0].uid,islands)
        self.world.add_islands(islands)
        self.world.add_forces(forces)
        
        
        islands = self.create_islands_in_area(0,750,480,50,1,1,(30,),0,0) 
        forces = self.create_island_forces(30,players[0].uid,islands)   
        self.world.add_islands(islands)
        self.world.add_forces(forces)
        
        forts = self.create_islands_in_area(0,360,240,80,B_FORT,1,(30,60),80,100)
        fort_forces = self.create_island_forces(10,-1,forts)
        self.world.add_islands(forts)
        self.world.add_forces(fort_forces)
        
        missile_islands = self.create_islands_in_area(0,360,240,80,B_MISSILE,1,(10,),0,0)
        missile_forces = self.create_island_forces(random.randint(30,40),-1,missile_islands)
        self.world.add_islands(missile_islands)
        self.world.add_forces(missile_forces)
        
        other_islands = self.create_islands_in_area(0,80,480,250,B_NORMAL,random.randint(4,6),(30,60,90,),0,0) 
        forces = []
        for island in other_islands:
            troops = int(island.max_troops * 0.8)
            force_type = F_NORMAL    
            force = Force(force_type,-1,island.x,island.y,troops,80,STAY,island,island)
            forces.append(force)
        
        other_islands = self.create_islands_in_area(0,470,480,250,B_NORMAL,random.randint(4,6),(30,60,90,),0,0) 
        
        self.world.add_islands(other_islands)
        self.world.add_forces(forces)   
    
    def create_islands_in_area(self,x,y,w,h,island_type,total,troops_choice,gun_radius,gun_life):
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
                    islands.append(Island(island_type,ix,iy,troops,gun_radius,gun_life))
                    break
        
        return islands      
                   
        
    def create_island_forces(self,max_troops,uid,islands):    
        total = 0
        random_islands = []
        random_islands.extend(islands)
        random.shuffle(random_islands)
        forces = []
        for island in random_islands:
            if total < MAX_TROOPS:
                troops = int(island.max_troops * 0.8)
                if troops + total > max_troops:
                    troops = MAX_TROOPS - total
                if island.island_type == B_MISSILE:
                    force_type = F_MISSILE    
                else:
                    force_type = F_NORMAL
                force = Force(player.force_type,uid,island.x,island.y,troops,80,STAY,island,island)
                forces.append(force)
                total += troops
            else:
                troops = int(island.max_troops * 0.8)
                if island.island_type == B_MISSILE:
                    force_type = F_MISSILE    
                else:
                    force_type = F_NORMAL  
                force = Force(force_type,-1,island.x,island.y,troops,30,STAY,island,island)
                forces.append(force)
        return forces        


    def create_islands_3X2(self):
        pass
        
    def create_islands_2X2(self):
        pass



class Var:
    MISSILE_RADIUS = 80

       
        
class IslandGame:
    # 初始化游戏对象
    def __init__(self,manager,game_type,code,map_id = -1):
        self.id = game_id.get()
        self.code = code
        self.game_type = game_type
        self.players = {}
        self.robot_player = Player(-1,-1,"lxk",100,-1,2,None)
        self.world = None
        self.manager = manager
        self.sender = EventSender(self.manager,self)
        self.is_over = False
        self.map_id = map_id

    # 游戏对象中是否存在指定房号code
    def has_code(self):
        return self.code != None

    # 游戏是否结束，默认True
    def game_over(self):    
        self.is_over = True

    # 导弹攻击岛屿处理
    def handle_missile_attack_island(self,missile_force,island_force):
        forces = []
        # 遍历获取军队数据
        for force in self.world.forces.values():
            if force.force_type != F_NORMAL or force.id == missile_force.id or force.id == island_force.id:
                continue
            if force.is_intersects_circle(missile_force.dst_island.x,missile_force.dst_island.y,Var.MISSILE_RADIUS):
                forces.append(force)

        # 被攻击岛屿为一般岛屿类型时的处理
        if island_force.force_type == F_NORMAL:
            island_force.troops = 0 if island_force.troops <= missile_force.troops * 10 else island_force.troops - missile_force.troops * 10
        # 被攻击岛屿为导弹岛屿类型时的处理
        elif island_force.force_type == F_MISSILE:
            island_force.troops = 0 if island_force.troops <= missile_force.troops else island_force.troops - missile_force.troops

        for force in forces:
            force.troops -= random.randint(1, 10)
            force.troops = 0 if force.troops < 1 else force.troops
            if force.troops == 0:
                # 如果被攻击岛屿为0了，就删除掉该岛屿的军力
                self.world.remove_force(force.id)

        missile_force.troops = 0
        # 删除发射导弹的军队
        self.world.remove_force(missile_force.id)
        # 导弹攻击岛屿事件
        self.sender.missile_attack_event(self, missile_force, island_force, forces)

    # 攻击导弹岛屿处理
    def handle_attack_missile_base(self,force,missile_force):
        player = self.get_player(force.uid)
        missile_player = self.get_player(missile_force.uid)

        if missile_player != None and player != None and player.team == missile_player.team:
            force.go_back()     
        else:    
            if missile_force.troops >= 1 and missile_force.troops >= force.troops / 10.0 :
                missile_force.dec_troops(force.troops / 10.0)
                force.troops = 0
                self.world.remove_force(force.id)
            else:
                force.dec_troops(missile_force.troops * 10.0,self.world)
                if force.troops != 0:
                    force.go_back()
                missile_force.troops = 0
                missile_force.uid = force.uid
                
            
        self.sender.attack_missile_base_event(self, force, missile_force)

    # 攻击一般岛屿处理
    def handle_attack_island(self,force,island_force):
        #print "---> fight with island team"
        int_force = int(force.troops)
        int_island_force = int(island_force.troops)
        
        if int_force > int_island_force:
            self.world.remove_force(island_force.id)
            force.troops = (force.troops - island_force.troops) * random.randint(70, 100) / 100
            island_force.troops = 0
            if force.troops <= 0:
                self.world.remove_force(force.id)
            else:
                force.move_type = STAY
                force.src_island = force.dst_island
                force.x = force.src_island.x
                force.y = force.src_island.y    
        else:
            island_force.troops = (island_force.troops - force.troops) * random.randint(70, 100) / 100
            force.troops = 0
            self.world.remove_force(force.id)
   
        self.sender.fight_in_island_event(self,force,island_force)

    # 空中相遇处理
    def handle_fight_in_air(self,force,other_force):
        # 获取空中相遇的两对军队
        int_force = int(force.troops)
        int_other_force = int(other_force.troops)

        if int_force > int_other_force:
            dead = other_force.troops * 0.7 * random.randint(90, 110) / 100
            other_force.troops -= dead
            if other_force.troops <= 0:
                self.world.remove_force(other_force.id)
            force.troops -= dead * random.randint(60, 90) / 100
        elif int_force < int_other_force:
            dead = force.troops * 0.7 * random.randint(90, 110) / 100
            force.troops -= dead
            if force.troops <= 0:
                self.world.remove_force(force.id)
            other_force.troops -= dead * random.randint(60, 90) / 100
        else:
            dead = force.troops * 0.7 * random.randint(90, 110) / 100
            other_force.troops -= dead * random.randint(60, 90) / 100
            force.troops -= dead * random.randint(60, 90) / 100   
            if force.troops <= 0:
                self.world.remove_force(force.id)
            if other_force.troops <= 0:
                self.world.remove_force(other_force.id)    

        self.sender.fight_in_air_event(self,force,other_force)

    # 完成处理
    def check_game_result(self):
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
        
        if has_two_team:
            return False,-1
        
        return True,only_uid

    # 堡垒处理
    def handle_fort_island(self):
        fort_island = None
        for _,island in self.world.islands.items():
            if island.island_type == B_FORT or island.gun_life > 0:
                fort_island = island
                island_forces = [force for force in self.world.forces.values() if force.src_island.id == fort_island.id and force.move_type == STAY]
                island_force = None if len(island_forces) == 0  else island_forces[0]
                break       
                
        if fort_island != None and time.time() - fort_island.last_attack > 1:   
            if island_force == None or island_force.uid < 0:
                return
            
            forces = []
            fort_player = self.get_player(island_force.uid)
            for force in self.world.forces.values():
                if force.move_type != MOVE or force.force_type != F_NORMAL:
                    continue
                force_player = self.get_player(force.uid)
                if force_player != None and fort_player.team == force_player.team:
                    continue
                
                if force.is_intersects_circle(fort_island.x,fort_island.y,fort_island.gun_radius):
                    forces.append(force)
            
            if len(forces) == 0:
                return  
            
            force = random.choice(forces)
            r = random.randint(0,99)
            if r < 20:
                dead = 0
            elif r < 40:
                dead = 1
            elif r < 60:
                dead = 2                
            else:
                dead = 3
            
            fort_island.gun_life -= dead
            fort_island.last_attack = time.time()

            force.troops = 0 if force.troops <= dead else force.troops - dead
            if force.troops == 0:
                self.world.remove_force(force.id)
            
            self.sender.fort_attack_event(self, fort_island, force, dead)

    # 游戏运行中处理
    def run(self):
        loop_duration = 0.1           # 循环间隔，单位秒
        begin = int(time.time())      # 记录开始时间
        winner = -1                   # 胜利者
        self.is_over = False          # 已结束
        last_time = time.time()       # 上次执行的时间

        # 游戏没有结束或者运行时间没有超过20分钟(1200秒)就继续循环
        while not self.is_over and (time.time() - begin) < 1200:
            duration = time.time() - last_time
            last_time = time.time()

            # 增长行动力
            for player in self.players.values():
                if player.power <= 100:
                    player.power += 5 * duration
                #print "player.power",player.uid,player.power

            # 军队数据
            forces = self.world.forces.values()
            # 随机军队数据
            random.shuffle(forces)
            for force in forces:
                # 军力移动状态为静止时
                if force.move_type == STAY:
                    island = self.world.get_island(force.src_island.id)
                    # 军力增长处理
                    force.stay(island,duration)
                    continue

                # 军力移动时的处理
                force.move(duration)
                # 军力到达目的地时的处理
                if not force.is_reachs_destination():
                    continue    
                
                island_force = self.world.get_island_stay_force(force.dst_island.id)
                # 先处理导弹
                if force.force_type == F_MISSILE:
                    self.handle_missile_attack_island(force,island_force)
                    continue
                # 攻击导弹岛屿
                if force.dst_island.island_type == B_MISSILE:
                    self.handle_attack_missile_base(force,island_force)
                    continue
                
                if island_force == None:
                    force.move_type = STAY
                    force.src_island = force.dst_island
                    force.x = force.dst_island.x 
                    force.y = force.dst_island.y
                    self.sender.update_force_event(self,force)
                # 1. 同一个用户：合并
                elif force.uid == island_force.uid:   
                    #island_force.morale = (island_force.morale * island_force.troops + force.morale * force.troops) / (island_force.troops + force.troops)
                    troops = island_force.troops + force.troops
                    island_force.set_troops(troops)
                    self.world.remove_force(force.id)
                    self.sender.merge_force_event(self,island_force,force)
                # 2. 不同用户，同一个组:合并   
                elif self.get_player(force.uid).team == self.get_player(island_force.uid).team:
                    if island_force.troops < force.troops:
                        island_force.uid = force.uid
                        
                    troops = island_force.troops + force.troops
                    island_force.set_troops(troops)
                    self.world.remove_force(force.id)
                    self.sender.merge_force_event(self,island_force,force)
                    
                # 3. 不同用户，战斗
                elif self.get_player(force.uid).team != self.get_player(island_force.uid).team:
                    self.handle_attack_island(force,island_force)

            # 堡垒处理
            self.handle_fort_island()

            # 处理空中相遇战斗
            forces = self.world.forces.values()
            for k,force in enumerate(forces):
                if force.troops <= 0 or force.force_type == F_MISSILE:
                    continue
               
                for j in range(k+1,len(forces)):
                    other_force = forces[j]
                    if other_force == None or other_force.force_type == F_MISSILE or other_force.troops <= 0 or force.troops <= 0:
                        continue
                        
                    if force.move_type == STAY or other_force.move_type == STAY:
                        continue    
                    if not other_force.is_intersects_circle(force.x,force.y,force.radius):
                        continue
                    # 不同用户，且不是同一个组: 战斗
                    if self.get_player(force.uid).team != self.get_player(other_force.uid).team:
                        self.handle_fight_in_air(force,other_force)
                                 
            #if random.randint(1,100) > 95:
            #    self.test_ai()    
            #    print "---create force now ->"
        
            is_over,winner = self.check_game_result()
            if is_over:
                break
            
            gevent.sleep(loop_duration)
    
        if winner < 0:
            name = ""
        else:    
            player = self.get_player(winner)
            name = player.name
        self.sender.game_over_event(self,winner,name)            
        self.manager.remove_game_since_over(self.id)

    # 创建游戏世界
    def create_world(self):
        # 游戏世界创建者
        world_creator = WorldCreator()
        # 构造一个480*800尺寸的游戏世界
        self.world = World(480,800)
        # 游戏世界创建者创建一个游戏地图
        # 返回游戏地图的id
        self.map_id = world_creator.create_by_map(self.manager.redis,self.map_id,self.game_type,self.world,self.players.values())

        #if self.game_type == G1X1:
        #    world_creator.create_by_map(self.manager.redis,1,self.world,self.players.values())
        #else:
        #    raise Exception("No this kind of game") 
        #print "------> create world", self.map_id

        gevent.spawn(self.run)

    # 创建军队，玩家点击，从a点飞到b点
    def create_force(self,uid,src_island_id,dst_island_id,troops,move_type):
        # 获取玩家数据
        player = self.players.get(uid)
        if player == None:
            return None
        # 获取出生岛和目标岛的数据
        src_island = self.world.get_island(src_island_id)
        dst_island = self.world.get_island(dst_island_id)

        # 判断玩家飞到路上的飞机
        player_forces = [f for f in self.world.forces.values() if f.uid == uid and f.move_type != STAY]

        # if len(player_forces) >= player.power:
        #    # 如果玩家的在路上的飞机大于等于玩家限制飞机数就直接返回
        #    return None
        # 判断玩家需要飞出去的数量是否大于所属岛屿上的数量
        island_force = self.world.get_island_my_stay_force(uid,src_island_id)



        if island_force == None or island_force.troops < troops:
            return None
        # 判断航线是否存在
        if island_force.force_type == F_NORMAL and src_island.lines.get(dst_island_id) == None:
            return None

        # 发出岛屿类型
        force_type = island_force.force_type
        # new一个飞出的军队
        force = Force(force_type,uid,island_force.x,island_force.y,troops,island_force.morale,move_type,src_island,dst_island)
        #　添加至游戏数据中
        self.world.add_force(force)
        # 飞出到的军队数 - 飞出的军队数
        new_troops = island_force.troops - troops
        # 设置飞出到的军队数据（飞出后的数据）
        island_force.set_troops(new_troops)
        # 如果飞出后岛屿军队数据为0，就删除掉军队数据
        if island_force.troops == 0:
            self.world.remove_force(island_force.id)

        # 减去行动力 todo.x
        if island_force.force_type == F_NORMAL:
            if player.power < 20:
                return None
            player.power -= 20
        elif island_force.force_type == F_MISSILE:
            if player.power < 30:
                return None
            player.power -= 30

        # 发送事件
        self.sender.new_force_event(self,force,island_force)        
        return force

    # 验证游戏数据中是否存在指定uid的用户，返回bool
    def has_player(self,uid):
        return uid in self.players

    # 向游戏世界中添加用户对象
    def add_player(self,uid,access_id,name,team,power,commander):
        # 验证游戏世界中是否存在该用户
        if uid in self.players:
            # 存在该用户就设置该用户在线，并返回该用户uid
            self.players[uid].is_online = True
            return uid

        # 验证用户数大于游戏用户类型限制的人数
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
        
                
        player = Player(uid,access_id,name,team,len(self.players),power,commander)
        self.players[player.uid] = player
        # 准备完成，创建游戏数据
        if self.is_ready():
            self.create_world()
        return 0

    # 游戏世界中删除用户对象
    def remove_player(self,uid):
        if self.is_ready():
            return False
        self.players.pop(uid,None)

    # 判断是否准备完成，返回bool
    def is_ready(self):
       
        if self.game_type == G1X1:
            return len(self.players) == 2
        elif self.game_type == G1X2:
            return len(self.players) == 3
        elif self.game_type == G2X2:
            return len(self.players) == 4
        elif self.game_type == G3X0:
            return len(self.players) == 3
        elif self.game_type == G4X0:
            return len(self.players) == 4      
        return False

    # 根据uid获取用户对象
    def get_player(self,uid):
        if uid < 0:
            return self.robot_player
        return self.players.get(uid)

    # 获取除了传入uid的所有用户数据
    def get_player_uids(self,except_one):
        uids = []
        for player in self.players.values():
            if player.uid >= 0 and player.uid != except_one:
                uids.append(player.uid)
        return uids
        
    # 设置游戏状态为protobuf格式
    def set_proto_game_state(self,state):
        state.game_id = self.id
        for player in self.players.values():
            state.players._values.append(player.get_proto_struct())
        return state


class EventSender:
    def __init__(self,manager,game):
        self.manager = manager
        self.game = game

    def set_power(self,game,event):
        for player in game.players.values():
            pb_power = event.body.player_powers.add()
            pb_power.uid = player.uid
            pb_power.power = int(player.power)

    def new_force_event(self,game,force,island_force):
        event = create_client_event(NewForceEvent)
        force.get_proto_struct(event.body.new_force)
        island_force.get_proto_struct(event.body.island_force)
        event.body.server_time = int(time.time() * 1000)
        event.body.game_id = game.id

        self.set_power(game,event)

        if self.manager:
            self.manager.notify_game_players(event,self.game)        

    def update_force_event(self,game,force):
        event = create_client_event(UpdateForceEvent)
        force.get_proto_struct(event.body.force)
        event.body.server_time = int(time.time() * 1000)
        event.body.game_id = game.id
        self.set_power(game,event)
        if self.manager:
            self.manager.notify_game_players(event,self.game)        

    def merge_force_event(self,game,target_force,force):
        event = create_client_event(MergeForceEvent)
        target_force.get_proto_struct(event.body.target_force)
        force.get_proto_struct(event.body.force)
        event.body.server_time = int(time.time() * 1000)
        event.body.game_id = game.id
        self.set_power(game,event)
        if self.manager:
            self.manager.notify_game_players(event,self.game)        
    
    def attack_missile_base_event(self,game,force,missile_force):
        event = create_client_event(AttackMissileBaseEvent)
        event.body.server_time = int(time.time() * 1000)
        missile_force.get_proto_struct(event.body.island_force)
        force.get_proto_struct(event.body.force)
        
        event.body.game_id = game.id
        self.set_power(game,event)
        if self.manager:
            self.manager.notify_game_players(event,self.game)

    def missile_attack_event(self,game,missile_force,island_force,forces):
        event = create_client_event(MissileAttackEvent)
        event.body.server_time = int(time.time() * 1000)
        missile_force.get_proto_struct(event.body.missile_force)
        island_force.get_proto_struct(event.body.island_force)
        for force in forces:
            pb_force = event.body.forces.add()
            force.get_proto_struct(pb_force)
        event.body.game_id = game.id
        self.set_power(game,event)
        if self.manager:
            self.manager.notify_game_players(event,self.game) 

    def fort_attack_event(self,game,island,target_force,dead):
        event = create_client_event(FortAttackEvent)
        event.body.server_time = int(time.time() * 1000)
        target_force.get_proto_struct(event.body.force)
        event.body.game_id = game.id
        event.body.island_id = island.id
        event.body.gun_life = island.gun_life
        event.body.dead = dead
        self.set_power(game,event)
        if self.manager:
            self.manager.notify_game_players(event,self.game) 
    
    def fight_in_island_event(self,game,force,island_force):
        event = create_client_event(FightInIslandEvent)
        island_force.get_proto_struct(event.body.island_force)
        force.get_proto_struct(event.body.force)
        event.body.server_time = int(time.time() * 1000)
        event.body.game_id = game.id
        self.set_power(game,event)
        if self.manager:
            self.manager.notify_game_players(event,self.game)                
        
    def fight_in_air_event(self,game,force,other_force):
        event = create_client_event(FightInAirEvent)
        other_force.get_proto_struct(event.body.other_force)
        force.get_proto_struct(event.body.force)
        event.body.server_time = int(time.time() * 1000)
        event.body.game_id = game.id
        self.set_power(game,event)
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
    
    