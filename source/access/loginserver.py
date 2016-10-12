#coding:utf-8

import gevent
from gevent import monkey;monkey.patch_all()

from gevent.server import StreamServer
from gevent.pool import Pool
from gevent.queue import Queue
import httplib,urllib
import signal 
import json

import logging
import traceback
import time
import os,sys
import random

from systemconfig import *

from proto.access_pb2 import *
from message.base import *
from message.resultdef import *

import redis

from db.connect import *
from db.account import *
from util.asyncsocket import *

pool = Pool(50)

def random_session():
    return random.randint(10000000,20000000)
    

CLIENT_TIMEOUT = 60
BUFFER_SIZE = 1024


class VersionManager:
    def __init__(self):
        with open("../version/VERSION") as f:
            self.version = int(f.readline())
        self.upgrade_info = {}
        gevent.spawn(self.load_version)
        
    def load_version(self):        
        with open("../version/VERSION") as f:
            self.version = int(f.readline())                
        gevent.sleep(60)
        
    def get_upgrade_info(self,old_version):
        if self.version <= old_version:
            return None
        key = self.version
        json = self.upgrade_info.get(key,None)
        if json == None:
            version_file = "../version/verinfo_" + str(self.version) + ".json"
            with open(version_file) as f:
                json = f.read()
      
            self.upgrade_info[key] = json
        return json         

class LoginServer:
    def __init__(self,conf):
        self.conf = conf
        self.accounts = {}
        self.redis = redis.Redis(*conf.get_redis_config("login_redis"))
        
        self.message_handlers = {
            RegisterReq.DEF.Value("ID"):self.handle_register,
            LoginReq.DEF.Value("ID"): self.handle_login,
            LogoutReq.DEF.Value("ID"): self.handle_logout,
            CheckUpgradeReq.DEF.Value("ID"):self.handle_check_upgrade,
        }
        self.version_manager = VersionManager()
    
    def init(self):
        logging.info("Check account table ...")
        session = UserSession()
        try:
            session.begin()
            row = session.execute("show table status where name = 'account'").fetchone()
            auto_increment = row["Auto_increment"]
            if auto_increment < 10000:
                session.execute("alter table account auto_increment = 10000")
            session.commit()
        except:
            traceback.print_exc()
            session.rollback()
        finally:
            session.close()
            session = None
    
    def handle_client_socket(self,sock,address):
        #logging.info("------------>" + str(sock) + "------->" + str(address))
        logging.info("=====>> new client is comming ...")
        sock.settimeout(CLIENT_TIMEOUT)
        sock = async_send_socket(sock)
        buffer = ""
        while True:
            try :
                request_data = get_message(buffer,len(buffer),0)
                if request_data == None:
                    data = sock.recv(BUFFER_SIZE)
                    if data == None or len(data) == 0:
                        logging.info("disconnected now ---> no data")
                        break
                    buffer += data
                    continue
                msg,start = request_data
                buffer = buffer[start:]
                handler = self.message_handlers.get(msg.header.command)
                if handler == None:
                    logging.info("receive invalid message" + str(msg.header.command))
                    break
                logging.info("receive a client message:" + str(msg.body))
                resp = create_response(msg)
                connect = handler(msg,resp)
                logging.info("send a message back to client: %d,%d " + str(resp.body),resp.header.result,resp.header.user)
                sock.async_send(resp.encode())
                #if connect == True:
                #     continue
                break
            except:
                traceback.print_exc()
                break
        sock.async_close()
        
            
    def handle_check_upgrade(self,message,resp):
        old_version = message.body.version
        version_info = self.version_manager.get_upgrade_info(old_version)
        resp.body.version = self.version_manager.version
        if version_info != None: 
            resp.body.upgrade_info = version_info
        resp.header.result = 0
        return True
        
    def handle_register(self,message,resp):
        session = UserSession()
        try :
            session.begin()
            account = session.query(TAccount).with_lockmode("update").filter(TAccount.account == message.body.account).first()
            if account != None:
                resp.header.result = RESULT_FAILED_NAME_EXISTED
                return  
                
            account = message.body.account.strip()
            
            if account.startswith("_robot_") or len(account) < 6 or len(account) > 11:
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID 
                return 
            
            if len(message.body.account.strip()) == 0 :
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
                return    
                
            if len(message.body.password) < 6:
                resp.header.result = RESULT_FAILED_PASSWORD_INVALID
                return 
            
            account = TAccount()
            account.account = message.body.account
            account.password = message.body.password
            account.state = 1
            account.create_time = int(time.time())
             
            session.add(account)    
            session.commit()
                        
            random_key = random_session()
            resp.body.accountid = account.id
            resp.body.session = random_key
            
            id,ip,port = self.get_idle_server()
            
            resp.body.server.id = id
            resp.body.server.ip = ip
            resp.body.server.port = port
                
            resp.header.result = 0
            
            self.redis.hset("sessions",account.id,random_key)
        except:
            traceback.print_exc()
            session.rollback()          
        finally :
            if session != None:
                session.close()
        return True
        
    def get_idle_server(self):
        keys = self.redis.keys("server*")
        
        id = 0
        ip = ''
        port = 0
        users = 1000000
       
        for k in keys:
            s_id,s_ip,s_port = self.redis.hmget(k,"id","ip","port")
            s_users = self.redis.hlen(k) - 3      
            if s_users <= users:
                id,ip,port,users = s_id,s_ip,s_port,s_users
        return int(id),ip,int(port)
                
    def handle_check_account(self,message,resp):
        session = UserSession()
        try :
            account = session.query(TAccount).with_lockmode("update").filter(TAccount.name == message.body.account).first()
            if account != None:
                resp.header.result = RESULT_FAILED_NAME_EXISTED
                return  
            account = message.body.account.strip()
                
            if account.startswith("_robot_") or len(account) < 6 or len(account) > 11:
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID 
                return 
            
            if len(message.body.account.strip()) == 0 :
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
                return    
            resp.header.result = 0    
        except:
            traceback.print_exc()            
        finally :
            if session != None:
                session.close()
        
        return True    
    
    def handle_login(self,message,resp):
        if message.body.account.strip().startswith("_robot_"):
            resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
            return 
            
        session = UserSession()

        try :
            session.begin()
            account = session.query(TAccount).filter(TAccount.account == message.body.account).first()
            if account == None :
                resp.header.result = RESULT_FAILED_ACCOUNT_INVALID
                return 
            
            if account.password != message.body.password:
                resp.header.result = RESULT_FAILED_PASSWORD_INVALID
                return  
                        
            random_key = random_session()
            self.accounts[account.id] = random_key
            resp.body.accountid = account.id
            resp.body.session = random_key
            
                
            id,ip,port = self.get_idle_server()
            
            resp.body.server.id = id
            resp.body.server.ip = ip
            resp.body.server.port = port
                
            resp.header.result = 0
            session.commit()
            
            self.redis.hset("sessions",account.id,random_key)
        except:
            traceback.print_exc()
            session.rollback()          
        finally :
            if session != None:
                session.close()

    
        
        
    def handle_logout(self,message,resp):
        try :
            resp.header.result = 0 
            self.redis.hdel("sessions",account.id,random_key)
        finally :
            return
        
    
                
    
if __name__ == "__main__":
    
    MessageMapping.init()
    
    conf = SystemConfig("system.ini",None)   
    DATABASE.setup_user_session(*conf.get_database_config("userdb"))
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = conf.system_config.getint("system","login_port")
        
    logging.basicConfig(level=logging.DEBUG,                        
                        format='%(threadName)s:%(asctime)s %(levelname)s %(message)s',
                        stream=sys.stdout,
                        filemode='a')
    
    threads = []
    login_server = LoginServer(conf)    
    login_server.init()
    threads.append(gevent.spawn(StreamServer(('0.0.0.0', port), login_server.handle_client_socket).serve_forever))
    logging.info("Login Server System Started on port=%d",port)
    
    _queue = Queue()    
    
    def quit():
        _queue.put_nowait(None)
    
    gevent.signal(signal.SIGINT,quit)
    
    _queue.get()
    logging.info("====> Login Server Quit <====")