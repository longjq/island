#coding: utf-8

import gevent
from gevent import monkey;monkey.patch_all()

import redis

from gevent.pool import Pool
from gevent.server import StreamServer
from gevent.queue import Queue

from threading import Lock
import binascii
import logging
import traceback, copy
import time
from ctypes import *

from message.base import *
from message.resultdef import *
from proto.access_pb2 import *

from config import var

LOGOUT_RESP_ID = LogoutResp.DEF.Value("ID")
CONNECT_GAME_SERVER_REQ_ID = ConnectGameServerReq.DEF.Value("ID")

CLIENT_TIMEOUT = 600
MAX_CONNECTIONS = 400
LOOP_PERIOD = 60

_close_client = object()

class AccessClientConnection(object):
    _ID_BEGIN = 0x40000000
    _ID_END = 0x90000000
    def __init__(self,access_server,sock):
        self.access_server = access_server
        self.user = -1
        self.sock = sock
        self.is_safe = False
        self.transactions = {}
        self._transaction = AccessClientConnection._ID_BEGIN
        
        self.login_time = 0
        self.heartbeat_time = 0
        self.session = None
        self.connection_id = "%d-%d" % (self.access_server.access_service.serviceId,time.time())
        
        self._lock = Lock()
        self._receive_queue = Queue()
        self._send_queue = Queue()
        self._closed = False
        
        gevent.spawn(self._run_receive)
        gevent.spawn(self._run_send)
        
    def generate_transaction_id(self):
        #self._lock.acquire()
        self._transaction += 1
        if self._transaction >= AccessClientConnection._ID_END:
            self._transaction = AccessClientConnection._ID_BEGIN
        tmp = self._transaction
        #self._lock.release()
        return tmp
    
    def send(self,msg):
        self._send_queue.put_nowait(msg)
    
    def handle_message(self,msg):
        self._receive_queue.put_nowait(msg)    
    
    def _run_receive(self):
        _queue = self._receive_queue
        while True:
            msg = _queue.get()
            if msg == _close_client:
                self.sock.close()
                break
            self.on_message(msg)
    
    def _run_send(self):
        _queue = self._send_queue
        while True:
            msg = _queue.get()
            if msg == _close_client:
                self.sock.close()
                break
            if var.DEBUG:
                request,idx = get_message(msg)
                logging.info("send a message back: cmd=%d | user=%d | result=%d " %(request.header.command,request.header.user,request.header.result))
                logging.info("message body:" + str(request.body))
            try :
                self.sock.sendall(msg)
            except:
                pass
    
    def close(self):
        if self._closed:
            return 
        self.access_server.users.pop(self.user,None)
        self.handle_message(_close_client)
        self.send(_close_client)    
        self._closed = True
        
        req = create_client_message(QuitGameServerReq)
        req.header.user = self.user
        self.access_server.access_service.forward_message(req.header,req.encode())
        
        # 清除session，服务器负载信息，用户到接入服务器映射信息
        if self.session != None and self.access_server.redis.hget("sessions",self.user) == self.session:
            self.access_server.redis.hdel("sessions",self.user)
        if self.access_server.redis.hget("server" + str(self.access_server.server_id),self.user) == self.connection_id:
            self.access_server.redis.hdel("server" + str(self.access_server.server_id),self.user)
            self.access_server.redis.hdel("mapping",self.user)
        
        self.user = -1
            
    def connect_server(self,client_message):
        req,index = get_request(client_message.data)
                
        session = int(self.access_server.redis.hget("sessions",req.header.user))
        
        if session == req.body.session:
            self.heartbeat_time = int(time.time())
            self.is_safe = True
            self.user = req.header.user
            self.login_time = int(time.time())
            self.session = session
            
            old_connection = self.access_server.users.get(req.header.user,None)
            if old_connection != None:
                logging.info("Same user is logined so kick off previous one user = %d",req.header.user )
                old_connection.close()
                
            self.access_server.users[req.header.user] = self
            resp = create_client_message(ConnectGameServerResp)
            resp.header.user = req.header.user
            resp.header.result = 0
            resp.body.server_time = int(time.time())
            self.send(resp.encode())
            
            # 记录server的负载信息，用户到server的映射信息
            self.access_server.redis.hset("server" + str(self.access_server.server_id),req.header.user,self.connection_id)
            self.access_server.redis.hset("mapping",req.header.user,self.access_server.server_id)
        else:
            logging.info("login is failure ,so close it !" )
            resp = create_client_message(ConnectGameServerResp)
            resp.header.user = req.header.user
            resp.header.result = -1
            self.send(resp.encode())
            self.close()    
    
    def on_message(self,client_message):
    	request,idx = get_request(client_message.data)

        if var.DEBUG:
            logging.info("receive a message : cmd=%d | user=%d | len=%d " %(client_message.header.command,client_message.header.user,client_message.header.length))
            logging.info("message body:" + str(request.body))
        
        if not self.is_safe:
            if client_message.header.command != CONNECT_GAME_SERVER_REQ_ID:
                logging.info("the first message must be ConnectGamerServer , user = %d" + str(client_message.header.user))
                self.close()
            else:
                self.connect_server(client_message)
                
            return
        else:
            if client_message.header.command == CONNECT_GAME_SERVER_REQ_ID:
                self.connect_server(client_message)
                return 
                        
        result = self.on_safe_message(client_message)
        
        if result < 0:
            logging.info("result(%d) is failure and user = %d, it should not happen",result,client_message.header.user)
            self.close()
            
    def on_safe_message(self,client_message):           
        access_server = self.access_server
        # 检查是否安全登录过
        if (client_message.header.user not in access_server.users or client_message.header.user != self.user):
            logging.info("it should not happen,then close connection")
            self.close()
            return -1
            
        #logging.info("receive a client message :%d",client_message.header.command)
        self.transactions[client_message.header.transaction] = client_message
        # 转发至其它服务
        # 修改心跳时间
        self.heartbeat_time = int(time.time())
        access_server.access_service.forward_message(client_message.header,client_message.data)
        return 0


class AccessRawMessage:
    def __init__(self,header,data):
        self.header = header
        self.data = data
        self.receive_time = time.time()
        
    def get_message_data(self):
        return self.data 

        
class AccessServer:
    def __init__(self,server_id,conf,ip,port):
        self.conf = conf
        self.port = port
        self.server_id = int(server_id)
        # 管理经过鉴权的用户信息
        self.users = {}
       
        self.lock = Lock()        
        self.access_service = None
        pool = Pool(2000)
        
        self.redis = redis.Redis(*conf.get_redis_config("access_redis"))
        
        self.redis.delete("server" + str(self.server_id))
        self.redis.delete("queue" + str(self.server_id))
        self.redis.hmset("server" + str(self.server_id),{"id":self.server_id,"ip":ip,"port":port})
        
        gevent.spawn_later(20,self.check_connection)
        gevent.spawn(StreamServer(("0.0.0.0",self.port),self.handle_access_socket,spawn = pool).serve_forever)
        gevent.spawn(self.handle_queue)
        
    def handle_access_socket(self,sock,address):
        logging.info("a client connecting now .....")
        buffer = ""
        conn = AccessClientConnection(self,sock)
        try :
            while True:
                header = get_header(buffer,len(buffer),0)
                if header == None or header.length > len(buffer):
                    data = sock.recv(1024)
                    if data == None or len(data) == 0:
                        #logging.info("disconnected now ---> no data")
                        break
                    
                    buffer += data
                    continue
                msg = AccessRawMessage(header,buffer[:header.length])
                #logging.info("receive a message ==>" + str(msg))
                buffer = buffer[header.length:]
                conn.handle_message(msg)
        except:
            #traceback.print_exc()
            pass
        finally:
            conn.close()          
        

    def set_access_service(self, service):
        global MAX_CONNECTIONS
        self.access_service = service
        MAX_CONNECTIONS = int(service.getConfigOption("max_connections",1000))
        
    
    
        
    # 发送响应用户事件至客户端            
    def response_user_message(self, user, transaction,event_type, data):
        connection = self.users.get(user,None)
        if connection == None:
            logging.info("user %d is not exist:event_type = %d",user,event_type)
            return 
            
        if transaction in connection.transactions:
            client_message = connection.transactions.pop(transaction,None)
            connection.send(data)
        else:
            connection.send(data)
            return 
        
        if event_type == LOGOUT_RESP_ID:
            connection.close()
            
    
    def handle_queue(self):
        while True:
            try:
                #data = self.redis.brpoplpush("queue" + str(self.server_id),"queue_debug")
                _,data = self.redis.brpop("queue" + str(self.server_id))

                user,transaction,event_type = struct.unpack_from("llh",data)
                
                msg = data[struct.calcsize("llh"):]
                    
                connection = self.users.get(user,None)
                if connection == None:
                    logging.info("user %d is not exist:event_type = %d",user,event_type)
                    continue 
                    
                connection.send(msg)
                
                if event_type == LOGOUT_RESP_ID:
                    self.disconnect_client(user)   
            except:
                traceback.print_exc()
                pass
                              
        
    # 断开已经鉴权的客户端的连接    
    def disconnect_client(self, user):
        connection = self.users.pop(user,None)
        if connection != None:
            connection.close()
    
    def check_connection(self):
        while True:
            now = time.time()
            # 网络连接断连，心跳超时，或超时消息存在则断连
            for user, connection in self.users.items():
                client_message = None
                no_error = False
                for transaction, client_message in connection.transactions.items():
                    if now - client_message.receive_time > LOOP_PERIOD:
                        # 如出现异常消息，则直接断连
                        connection.transactions.pop(transaction,None)
                        logging.error(" user %d,message %d ,transaction %d is timeout",
                            client_message.header.user, client_message.header.command, client_message.header.transaction)
                        self.disconnect_client(client_message.header.user)    
                        break
                else:
                    no_error = True
            
            gevent.sleep(LOOP_PERIOD)