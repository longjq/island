#coding: utf-8
import gevent
from gevent.server import StreamServer
from gevent.queue import Queue

import binascii

import sys,logging
import struct
import traceback
from threading import Lock

# 握手协议：服务器之间在建立TCP后，首先进行握手，交换各自服务器名字
# 服务器名字应该小于20个字节
formatOfShakeHand = "<HH20s" # magic code + server name
lengthOfShakeHand = struct.calcsize(formatOfShakeHand)


# 服务器之间通讯包的消息头格式
# 通讯包头内容包括：
#   类型 ：消息类型，同步消息或异步消息
#   长度 ：取值为整个数据包的长度
#   发送者ID：取值为发送者服务ID
#   接受者ID：取值为接受者服务ID
#   类型：  取值为消息类型
#   事务ID：取值为事务ID，由发送服务器自动产生
#   附加参数1：
#   附加参数2：

# mode + length + src id + dst id + type + transactionId + param1 + param2 
formatOfHeader = "<HHHHllll" 
lengthOfHeader = struct.calcsize(formatOfHeader)

# 产生本服务器唯一的事务
tid = 0
idLock = Lock()

EVENT_MODE_ASYNC        = 0 # 异步消息
EVENT_MODE_SYNC_REQ     = 1 # 同步请求
EVENT_MODE_SYNC_RESP    = 2 # 同步响应 

def transactionId():
    global tid,idLock
    #idLock.acquire()
    tid = tid + 1
    tmp = tid
    #idLock.release()
    return tmp
    
# 服务器之间和服务之间传递的对象定义
class Event:
    def __init__(self,mode,length,sid,did,eventType,tid,param1,param2,eventData):
        self.mode = mode
        self.length = length
        self.srcId = sid
        self.dstId = did
        self.eventType = eventType
        self.tranId = tid
        self.param1 = param1
        self.param2 = param2
        self.eventData = eventData
    
    def toStream(self):
        length = len(self.eventData) + lengthOfHeader 
        return struct.pack(formatOfHeader,self.mode,length, \
                    self.srcId,self.dstId,self.eventType, \
                    self.tranId,self.param1,self.param2) + self.eventData
        
    @staticmethod
    def createEvent(sid,did,eventType,param1,param2,eventData):
        length = lengthOfHeader + len(eventData)
        return Event(EVENT_MODE_ASYNC,length,sid,did,eventType,transactionId(),param1,param2,eventData)
        
    @staticmethod
    def createSyncRequestEvent(sid,did,eventType,param1,param2,eventData):
        length = lengthOfHeader + len(eventData)
        return Event(EVENT_MODE_SYNC_REQ,length,sid,did,eventType,transactionId(),param1,param2,eventData)  
    
    @staticmethod
    def createSyncResponseEvent(sid,did,eventType,param1,param2,eventData,origEvent):
        length = lengthOfHeader + len(eventData)
        return Event(EVENT_MODE_SYNC_RESP,length,sid,did,eventType,origEvent.tranId,param1,param2,eventData)    
        
    @staticmethod
    def createExistedEvent(mode,length,sid,did,eventType,tid,param1,param2,eventData):
        return Event(mode,length,sid,did,eventType,tid,param1,param2,eventData)
    
    @staticmethod
    def createEventFromStream(data):
    	l = len(data)
        if l < lengthOfHeader:
            return (False,None)
        (mode,length,sid,did,eventType,tid,param1,param2) = struct.unpack_from(formatOfHeader,data)
        if l < length:
            return (False,None)
        return (True,Event.createExistedEvent(mode,length,sid,did,eventType,tid,param1,param2,data[lengthOfHeader:length]))

_close_connection = object()

class ClientConnection:
    def __init__(self,host,client_name,server_ip,port):
        self.client_name = client_name
        self.server_name = None
        self.host = host
        self.server_ip = server_ip
        self.port = port
        self.sock = None
        self.peer_address = None
        self.is_shakehand = False
        gevent.spawn(self._run)
        
        self._send_queue = Queue()
        gevent.spawn(self._run_send)
    
    def __repr__(self):
        return "ClientConnection:" + self.server_name
    
    def _run_send(self):
        _queue = self._send_queue
        while True:
            msg = _queue.get()
            if msg==_close_connection:
                break
            else:
                if self.sock != None:
                    self.sock.sendall(msg)
    
    def connectionMade(self):
        self.peer_address = self.sock.getpeername()
        self.send(struct.pack(formatOfShakeHand,20,7,self.client_name))
        self.buffer = "" 
        self.is_shakehand = False       

    def connectionLost(self,reason):
        self.host.setServiceConnection(self.server_name,None)
        self.peer_address = None
        self.server_name = None
    
    def dataReceived(self,data):
        if self.is_shakehand:
            self.buffer += data
            while True:     
                (result,event) = Event.createEventFromStream(self.buffer)
                if result:
                    self.buffer = self.buffer[event.length:]
                    self.host.handle_network_event(self,event)
                else:
                    return
        else:
            self.buffer += data
            if len(self.buffer) < lengthOfShakeHand:
                return
            (magicCode1,magicCode2,self.server_name) = struct.unpack(formatOfShakeHand,self.buffer[:lengthOfShakeHand])
            self.server_name = self.server_name.strip()
            self.host.setServiceConnection(self.server_name,self)
            self.buffer = self.buffer[lengthOfShakeHand:]
            self.is_shakehand = True
            logging.info("server(%s:%s) shake hand successful",self.getPeer(),self.server_name)
    
    def __del__(self):
        logging.info("client(%s) low level connection is deleted : ",self.getPeer())
        
    def getPeer(self):
        if self.peer_address != None:
            return self.peer_address
        return None
        
    def send(self,data):
        self._send_queue.put_nowait(data)
        
    def _run(self):
        while True:
            try :
                self.sock = gevent.socket.create_connection((self.server_ip,self.port),)
                self.connectionMade()
                while True:
                    data = self.sock.recv(1024)
                    if data == None or len(data) == 0:
                        # peer is closed
                        break
                    self.dataReceived(data)    
            except:
                #traceback.print_exc()
                if self.sock != None:
                    self.sock.close()
                    self.sock = None
                    self.connectionLost(-1)
            finally:
                if self.sock != None:
                    self.sock.close()
                    self.sock = None
                    self.connectionLost(None)
            logging.info("server is lost %s and try it again",self.server_name)
            gevent.sleep(1)

class ServerConnection:
    def __init__(self,host,server_name):
        self.host = host
        self.server_name = server_name
        self.client_name = None
        self.sock = None
        self.is_shakehand = False
        self.peer_address = None
        
        self._send_queue = Queue()
        gevent.spawn(self._run_send)
    
    def _run_send(self):
        _queue = self._send_queue
        while True:
            msg = _queue.get()
            if msg==_close_connection:
                break
            else:
                if self.sock != None:
                    self.sock.sendall(msg)        
    
    def connectionMade(self):
        self.peer_address = self.sock.getpeername()
        self.buffer = ""
        self.is_shakehand = False

    def connectionLost(self,reason):
        self.host.setServiceConnection(self.client_name,None)
        self.peer_address = None
        self.client_name = None
    
    def dataReceived(self,data):
        if self.is_shakehand:
            self.buffer += data
            while True:     
                (result,event) = Event.createEventFromStream(self.buffer)
                if result:
                    self.buffer = self.buffer[event.length:]
                    self.host.handle_network_event(self,event)
                else:
                    return
        else:
            self.buffer += data
            if len(self.buffer) < lengthOfShakeHand:
                return
            (magicCode1,magicCode2,self.client_name) = struct.unpack(formatOfShakeHand,self.buffer[:lengthOfShakeHand])
            self.client_name = self.client_name.strip()
            self.send(struct.pack(formatOfShakeHand,magicCode1,magicCode2,self.host.name))
            self.host.setServiceConnection(self.client_name,self)
            self.buffer = self.buffer[lengthOfShakeHand:]
            self.is_shakehand = True
            logging.info("server(%s:%s) shake hand successful",self.getPeer(),self.client_name)

    def __del__(self):
        logging.info("server(%s) low level connection is deleted : ",self.getPeer())
        
    def __repr__(self):
        return "ServerConnection:" + self.client_name
        
    def getPeer(self):
        if self.peer_address != None:
            return self.peer_address
        return None
        
    def send(self,data):
        self._send_queue.put_nowait(data)

    def handle(self,sock,address):
        try :
            self.sock = sock
            self.connectionMade()
            while True:
                data = self.sock.recv(1024)
                if data == None or len(data) == 0:
                    break
                self.dataReceived(data)    
        except:
            if self.sock != None:
                self.sock.close()
                self.sock = None
                self.connectionLost(-1)
        finally:
            if self.sock != None:
                self.sock.close()
                self.connectionLost(None)
            self._send_queue.put_nowait(_close_connection)
            
        logging.info("client is lost %s ",self.client_name)


class ConnectionFactory:
    def __init__(self,host,server_name):
        self.host = host
        self.server_name = server_name
    
    def create_client_connection(self,client_name,server_ip,port):
        return ClientConnection(self.host,client_name,server_ip,port)        
        
    def handle_server_connection(self,sock,address):
        ServerConnection(self.host,self.server_name).handle(sock,address)
        
    def start_server_connection(self,port):
        gevent.spawn(StreamServer(("0.0.0.0",port),self.handle_server_connection).serve_forever)
        
        

