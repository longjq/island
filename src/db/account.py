#coding:utf-8

"""
数据库连接管理
"""

__author__ = "liangxiaokai@21cn.com"
__version__ = "1.0"
__date__ = "2011/04/14"
__copyright__ = "Copyright (c) 2011"
__license__ = "Python"

from connect import *

from sqlalchemy import Table,Column,func
from sqlalchemy.types import  *
from sqlalchemy.ext.declarative import declarative_base

tab_account = Table("account", metadata,
                 Column("id", Integer, primary_key=True),
                 Column("account", String(24)),
                 Column("nick",String(40)),
                 Column("state", Integer),
                 Column("imei",String(45)),
                 Column("password",String(11)),
                 Column("create_time",Integer),
                 Column("first_login", Integer),
                 )
                 

                 
class TAccount(TableObject):
    def __init__(self):
        TableObject.__init__(self)
        
mapper_account = Mapper(TAccount,tab_account)       

if __name__=="__main__":
    pass