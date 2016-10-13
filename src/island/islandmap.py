#coding: utf-8
import random
import json
import logging
import traceback

from proto.constant_pb2 import *
from islandobject import *

import redis

def get_any_map(r,map_type):
    # logging.info('@@@@@@@@@@@@@@@@@@@@(maps_'+str(map_type)+')@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    keys = r.hkeys("maps_" + str(map_type))
    #print "-=-=-=->",keys,map_type
    id = int(random.choice(keys))
    return id
# 初始化地图数据
def setup_world(r,id,world,players):
    #print "0=====> map:",id
    # 从redis获取地图数据
    data = r.get("map" + str(id))
    # logging.info('@@@@@@@@@@@@@@@@@@@@(map'+str(id)+')@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    # 把Json格式字符串解码转换成Python对象
    map = json.loads(data)
    # 遍历岛屿数据
    for json_island in map["islands"]:
        gun_radius = -1 
        gun_life = -1
        # 判断岛屿类型，n=一般，m=导弹，f=要塞
        if json_island["type"] == "n":
            island_type = B_NORMAL
        elif json_island["type"] == "m":
            island_type = B_MISSILE
        elif json_island["type"] == "f":
            island_type = B_FORT
            # f=要塞，要塞类型有半径和生命值
            gun_radius = json_island["gun_radius"]
            gun_life = json_island["gun_life"]
        else:
            island_type = B_BORN

        # 岛屿位置
        x,y = json_island["x"],json_island["y"]
        # 岛屿最大承载数
        max_troops = json_island["max"]

        # 创建岛屿实例
        island = Island(json_island["id"],island_type,x,y,json_island["radius"],max_troops,gun_radius,gun_life)
        island.id = json_island["id"]

        # 游戏世界上添加一个岛屿实例
        world.add_island(island)

        # 军队类型
        force_type = F_MISSILE if island.island_type == B_MISSILE else F_NORMAL
        uid = -1
        x,y = island.x,island.y
        # 士气值
        morale = 100
        move_type = STAY
        src = island
        dst = island

        # 随机攻击数
        min_force = json_island["forces"][0]
        max_force = json_island["forces"][1]
        troops = random.randint(min_force, max_force)
        force = Force(force_type,uid,x,y,troops,morale,move_type,src,dst)
        # 添加军队数
        world.add_force(force)

    for json_line in map["lines"]:
        src_island = world.get_island(json_line["src"])
        dst_island = world.get_island(json_line["dst"])

        points = []

        if json_line.get("points") != None:
            for json_point in json_line["points"]:
                #x,y = map(int,json_point.split(","))
                x,y = json_point[0],json_point[1]

                points.append(LinePoint(x,y))    
        line = FlightLine(1,src_island,dst_island,points)
        src_island.lines[dst_island.id] = line
        dst_island.lines[src_island.id] = line
        world.flight_lines.append(line)

   
    tmp_players = [] 
    tmp_players.extend(players)
    random.shuffle(tmp_players)

    for i,player in enumerate(tmp_players):
        #print "born ",i,player
        json_born = map["born"][i]
        count = json_born["count"]
        places = json_born["places"]

        for _ in xrange(count):
            island_id = random.choice(places)
            force = world.get_island_stay_force(island_id)
            if force != None:
                force.uid = player.uid


def load_map(file):
    with open(file,"r") as f:
        map = json.loads(f.read())
        r = redis.Redis(db=5)
        map_id = map["info"]["id"]
        r.hset("maps_all",map_id,json.dumps(map["info"]))

        wars = map["info"]["war"].lower().split(",")

        for war in wars:
            if war == "1v1":
                map_type = G1X1
            elif war == "1v2":
                map_type = G1X2
            elif war == "2v2":
                map_type = G2X2
            elif war == "3v0":
                map_type = G3X0
            elif war == "4v0":
                map_type = G4X0                

            #print "====>",war,wars

            r.hset("maps_" + str(map_type),map_id,json.dumps(map["info"]))        

        r.set("map" + str(map_id),json.dumps(map))




data = """ 
{
    "info": {
        "id":1,
        "name": "僵持战1v1",
        "remark": "僵持",
        "type": "1",
        "size": [
            480,
            800
        ],
        "id": 4,
        "war": "1V1"
    },
    "islands": [
        {
            "id": 1,
            "type": "b",
            "x": 206,
            "y": 92,
            "max": 70,
            "radius": 25,
            "forces": [
                30,
                30
            ]
        },
        {
            "id": 2,
            "type": "b",
            "x": 228,
            "y": 714,
            "max": 70,
            "radius": 25,
            "forces": [
                30,
                30
            ]
        },
        {
            "id": 3,
            "type": "n",
            "x": 76,
            "y": 316,
            "max": 60,
            "radius": 30,
            "forces": [
                15,
                15
            ]
        },
        {
            "id": 4,
            "type": "n",
            "x": 256,
            "y": 237,
            "max": 60,
            "radius": 30,
            "forces": [
                20,
                20
            ]
        },
        {
            "id": 5,
            "type": "n",
            "x": 402,
            "y": 131,
            "max": 90,
            "radius": 45,
            "forces": [
                30,
                30
            ]
        },
        {
            "id": 6,
            "type": "n",
            "x": 87,
            "y": 590,
            "max": 90,
            "radius": 45,
            "forces": [
                30,
                30
            ]
        },
        {
            "id": 7,
            "type": "n",
            "x": 268,
            "y": 533,
            "max": 60,
            "radius": 30,
            "forces": [
                20,
                20
            ]
        },
        {
            "id": 8,
            "type": "n",
            "x": 414,
            "y": 432,
            "max": 60,
            "radius": 30,
            "forces": [
                15,
                15
            ]
        }
    ],
    "lines": [
        {
            "src": 1,
            "dst": 3,
            "points": [
                [
                    190,
                    132
                ],
                [
                    150,
                    180
                ],
                [
                    110,
                    210
                ],
                [
                    80,
                    270
                ]
        ]
        },
        {
            "src": 1,
            "dst": 4
        },
        {
            "src": 1,
            "dst": 5
        },
        {
            "src": 3,
            "dst": 4
        },
        {
            "src": 4,
            "dst": 5
        },
        {
            "src": 3,
            "dst": 6

        },
        {
            "src": 4,
            "dst": 7

        },
        {
            "src": 5,
            "dst": 8
        },
        {
            "src": 6,
            "dst": 7
        },
        {
            "src": 7,
            "dst": 8
        },
        {
            "src": 2,
            "dst": 6
         },
        {
            "src": 2,
            "dst": 7
        },
        {
            "src": 2,
            "dst": 8,
            "points": [
                [
                    280,
                    700
                ],
                [
                    340,
                    650
                ],
                [
                    370,
                    600
                ],
                [
                    397,
                    500
                ]
        ]
        }
    ],
    "born": [
        {
            "count": 1,
            "places": [
                1
            ]
        },
        {
            "count": 1,
            "places": [
                2
            ]
        }
    ]
}
"""
data1 = """
{
    "info": {
        "id":1,
        "remark": "四人地图",
        "name": "五角星战役",
        "war": "2V2,4V0",
        "type": "1",
        "id": 2,
        "size": [
            480,
            800
        ]
    },
    "islands": [
        {
            "max": 50,
            "radius": 25,
            "forces": [
                30,
                30
            ],
            "y": 50,
            "x": 240,
            "type": "b",
            "id": 9
        },
        {
            "max": 50,
            "radius": 25,
            "forces": [
                30,
                30
            ],
            "y": 750,
            "x": 240,
            "type": "b",
            "id": 10
        },
        {
            "max": 70,
            "radius": 30,
            "forces": [
                30,
                30
            ],
            "y": 180,
            "x": 90,
            "type": "n",
            "id": 1
        },
        {
            "max": 70,
            "radius": 30,
            "forces": [
                30,
                30
            ],
            "y": 180,
            "x": 390,
            "type": "n",
            "id": 2
        },
        {
            "max": 70,
            "radius": 30,
            "forces": [
                30,
                30
            ],
            "y": 620,
            "x": 90,
            "type": "n",
            "id": 3
        },
        {
            "max": 70,
            "radius": 30,
            "forces": [
                30,
                30
            ],
            "y": 620,
            "x": 390,
            "type": "n",
            "id": 4
        },
        {
            "gun_radius": 60,
            "max": 40,
            "gun_life": 60,
            "radius": 30,
            "forces": [
                20,
                20
            ],
            "y": 340,
            "x": 150,
            "type": "f",
            "id": 5
        },
        {
            "gun_radius": 60,
            "max": 5,
            "gun_life": 60,
            "radius": 30,
            "forces": [
                2,
                2
            ],
            "y": 340,
            "x": 330,
            "type": "m",
            "id": 6
        },
        {
            "gun_radius": 60,
            "max": 40,
            "gun_life": 60,
            "radius": 30,
            "forces": [
                20,
                20
            ],
            "y": 460,
            "x": 150,
            "type": "f",
            "id": 7
        },
        {
            "gun_radius": 60,
            "max": 5,
            "gun_life": 60,
            "radius": 30,
            "forces": [
                2,
                2
            ],
            "y": 460,
            "x": 330,
            "type": "m",
            "id": 8
        }
    ],
    "lines": [
        {
            "src": 1,
            "dst": 2
        },
        {
            "src": 1,
            "dst": 6
        },
        {
            "src": 9,
            "dst": 6,
            "points":[]
        },
        {
            "src": 9,
            "dst": 5
        },
        {
            "src": 7,
            "dst": 5
        },
        {
            "src": 6,
            "dst": 8
        },
        {
            "src": 2,
            "dst": 5
        },
        {
            "src": 8,
            "dst": 10
        },
        {
            "src": 7,
            "dst": 4
        },
        {
            "src": 7,
            "dst": 10
        },
        {
            "src": 3,
            "dst": 8
        },
        {
            "src": 3,
            "dst": 4
        }
    ],
    "born": [
        {
            "count": 1,
            "places": [
                9
            ]
        },
        {
            "count": 1,
            "places": [
                10
            ]
        }
    ]
}
"""

if __name__ == "__main__":
    """
    players = []
    
    players.append(Player(1,-1,"lxk",100,100,2,None))
    players.append(Player(2,-1,"wxy",100,1000,2,None))
    world = World(800,480)
    setup_world(world,players)

    for force in world.forces.values():
        print force.id,force.uid,force.src_island.id
    """  
    import sys

    load_map(sys.argv[1])  
