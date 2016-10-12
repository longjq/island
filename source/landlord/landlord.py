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


class PlayTurn:
    def __init__(self,player,skip,cards,cards_type):
        self.player = player
        self.skip = skip
        self.cards = cards
        self.cards_type = cards_type   

class Card:
    def __init__(self,type,number):
        self.type = type
        self.number = number
        self.c = self.display()
    
    def __repr__(self):
        return self.c + "[" + str(self.type) + "]"
        
    def display(self):
        if self.number in [3,4,5,6,7,8,9,10]:
            c = str(self.number)
        elif self.number == 11:
            c = "J"
        elif self.number == 12:
            c = "Q"
        elif self.number == 13:
            c = "K"
        elif self.number == 14: 
            c = "A"
        elif self.number == 15:
            c = "2"       
        elif self.number == 100:
            c = "W1"
        else:
            c = "W2"
                                
        return c
    
    def __cmp__(self,other):
        if other == None:
            return 1
        if cmp(self.number,other.number) == 0:  
            return cmp(self.type,other.type)
        return cmp(self.number,other.number)
        
    @staticmethod
    def pb2Cards(pb_cards):
        cards = []
        for card in pb_cards:
            cards.append(Card(card.type,card.number))
        return cards
         
    
    @staticmethod    
    def get_all_cards():
        cards = []
        for type in range(1,5):
            for number in range(3,16):
                cards.append(Card(type,number))
        cards.append(Card(0,100)) #
        cards.append(Card(0,101)) # 
        return cards              

    @staticmethod    
    def get_quick_cards():
        cards = []
        
        for number in [6,7,8,9,10,11,12,13,14,15]:
            for type in range(1,5):
                cards.append(Card(type,number))
        cards.append(Card(0,100)) #
        cards.append(Card(0,101)) #
        return cards

    @staticmethod
    def get_bomb_cards(howmany = 4):
        cards = []
        """
        bombs = []
        
        numbers = range(3,16)
        numbers.append(100)
        for i in howmany:
            c = random.choice()
            numbers.remove(c)
            bombs.append(c)
        """    
        for number in [6,7,8,9,10]:
            for type in range(1,5):
                cards.append(Card(type,number))
        for type in range(1,5):
            for number in [3,4,5,11,12,13,14,15]:
                cards.append(Card(type,number))        
                
        cards.append(Card(0,100)) #
        cards.append(Card(0,101)) #
        return cards

CARD_TYPE_ERROR     = -1
CARD_TYPE_1         = 1
CARD_TYPE_2         = 2
CARD_TYPE_3         = 3
CARD_TYPE_4         = 4
CARD_TYPE_ZHA       = 100
CARD_TYPE_SHUN      = 11
CARD_TYPE_LIANDUI   = 22
CARD_TYPE_FEIJI3    = 66
CARD_TYPE_FEIJI4    = 88

class CardsType:
    def __init__(self,type,number,total = 0):
        self.type = type
        self.number = number
        self.total = total

    def same_type(self,other):
        return self.type == self.type and self.total == self.total 

    def __cmp__(self,other):
        if other == None:
            return 1
        if self.same_type(other):
            return cmp(self.number,other.number)
        if self.type == CARD_TYPE_ZHA:
            return 1
        if other.type == CARD_TYPE_ZHA:
            return -1
        return 0    

    def __repr__(self):
        return "T-%d-%d-%d" % (self.type,self.number,self.total)

    @staticmethod
    def card1(number):
        return CardsType(CARD_TYPE_1,number,1)
    
    @staticmethod
    def card2(number):
        return CardsType(CARD_TYPE_2,number,2)    

    @staticmethod
    def card3(number,total):
        return CardsType(CARD_TYPE_3,number,total)
    
    @staticmethod
    def zha(number,total):
        return CardsType(CARD_TYPE_ZHA,number,total)
    
    @staticmethod
    def card4(number,total):
        return CardsType(CARD_TYPE_4,number,total)
     
    @staticmethod
    def shun(number,bring):
        return CardsType(CARD_TYPE_SHUN,number,total)  
        
    @staticmethod
    def liandui(number,total):
        return CardsType(CARD_TYPE_LIANDUI,number,total)
        
    @staticmethod
    def feiji3(number,total):
        return CardsType(CARD_TYPE_FEIJI3,number,total)          

    @staticmethod
    def feiji4(number,total):
        return CardsType(CARD_TYPE_FEIJI4,number,total) 
        
class Rule:
    def __init__(self):
        pass
    
    def get_cards_type(self,cards):
        cards.sort()
        for i,card in enumerate(cards):
            if i > 0 and cmp(cards[i],cards[i-1]) == 0:
                return None
        # 单张
        if len(cards) == 1:
            return CardsType.card1(cards[0].number)      
        
        # 对王
        if len(cards) == 2 and cards[0].number in [100,101] and cards[1].number in [100,101]:
            return  CardsType.zha(100)
            
        c = Counter([card.number for card in cards])
        
        # 两个，三个，四个
        if len(c) == 1:
            l = len(cards)
            if l == 2:
                return CardsType.card2(cards[0].number)
            elif l == 3:
                return CardsType.card3(cards[0].number,3)
            elif l == 4:
                return CardsType.zha(cards[0].number,4)        
        
        total = sum(c.values())
        number3 = [k for k,v in c.items() if v == 3]
        number4 = [k for k,v in c.items() if v == 4]
        
        d = c.values()
        d.sort()
        d = tuple(d)
        
        if len(number3) == 1:
            if d == (1,3) or d == (2,3):
               return CardsType.card3(min(number3),total)        
        elif len(number3) == 2:
            if total in (6,8) or d == (2,2,3,3):
                return CardsType.feiji3(min(number3),total)   
        elif len(number3) == 3:
            if total in (9,12) or d == (2,2,2,3,3,3):
                return CardsType.feiji3(min(number3),total) 
        elif len(number3) == 4 and total in (12,16):
            return CardsType.feiji3(min(number3),total)     
        
        
        if len(number4) == 1:
            if total == 6 or d == (2,2,4):
                return CardsType.card4(min(number4),total)    
        elif len(number4) == 2:
            if total == 12 or d == (2,2,2,2,4,4):
                return CardsType.feiji4(min(number4),total)      
                    
        if len(c) == len(cards) and len(c) >= 5:
            min_number = min(c.keys())
            max_number = max(c.keys())
            
            if sum(range(min_number,min_number + len(c))) == sum(c.keys()) and max_number < 15:
                return CardsType.shun(min_number,total)
            
        number2 = [k for k,v in c.items() if v == 2]    
        if len(number2) * 2 == len(cards) and len(number2) >= 3:
            min_number = min(number2)
            max_number = max(number2)
            
            if sum(range(min_number,min_number + len(number2))) == sum(number2) and max_number < 15:
                return CardsType.liandui(min_number,total)
                                    
        
        return None
            
        
    
        
class Player:
    def __init__(self,user):
        self.user = user
        self.cards = []
        
    def has_cards(self,cards):
        for card in cards:  
            exist = False  
            for c in self.cards:
                if c.type == card.type and c.number == card.number:
                    exist = True
                    break
            if not exist:
                return False
        return True
    
    def remove_cards(self,cards):
        for card in cards:  
            for c in self.cards:
                if c.type == card.type and c.number == card.number:
                    self.cards.remove(c)
                    break
                        
    def __repr__(self):
        self.cards.sort()
        self.cards.reverse()
        return "[" + str(self.user) + ']==>' + str(self.cards)
    
class Landlord:
    def __init__(self,user1,user2,user3):
        self.players = [Player(user1),Player(user2),Player(user3)]
        
        self.lord = None
        self.base = 0
        self.rate = 1
        self.leave_cards = []
    
        self.turns = []
        self.rule = Rule()
    
    def shuffle(self,cards):
        random.shuffle(cards)
        return cards
    
    def deal_normal(self):    
        self.leave_cards = self.shuffle(Card.get_all_cards())     
        
        while len(self.leave_cards) > 3:
            self.players[0].cards.append(self.leave_cards.pop())
            self.players[1].cards.append(self.leave_cards.pop())
            self.players[2].cards.append(self.leave_cards.pop())
            
    
    def deal_quick(self):   
        self.leave_cards = self.shuffle(Card.get_quick_cards()) 
        
        while len(self.leave_cards) > 3:
            self.players[0].cards.append(self.leave_cards.pop())
            self.players[1].cards.append(self.leave_cards.pop())
            self.players[2].cards.append(self.leave_cards.pop())

    def deal_bomb(self,cut = 10,deal = 9):
        # history = [x.cards for x in reversed(self.turns) if not x.skip]
        # cards = [y for x in history for y in x]
        cards = (Card.get_bomb_cards()) 
        
        for x in xrange(cut):
            i = random.randint(3,22)
            j = random.randint(32,54)    
            cards = cards[i:j] + cards[:i] + cards[j:]
            
        
        while len(cards) > 3:
            leave = len(cards) - 3
            
            if leave/3 > deal:
                t = deal
            else:
                t = leave/3 
            
            for i in xrange(t):        
                self.players[0].cards.append(cards.pop())
            for i in xrange(t):        
                self.players[1].cards.append(cards.pop())
            for i in xrange(t):        
                self.players[2].cards.append(cards.pop())                
        
        self.leave_cards = cards
    
    def get_player(self,user):
        return [player for player in self.players if player.user == user][0]
        
    def is_turn(self,player):
        if len(self.turns) == 0:
            return True
        
        last_player_index = self.players.index(self.turns[-1].player)    
        player_index = self.players.index(player) 
        
        return player_index - last_player_index == 1 or last_player_index - player_index == 2
    
    def play_cards(self,accountid,skip,cards):
        player = self.get_player(accountid)
        if not self.is_turn(player):
            raise Exception("It is not your turn")
            
        if skip and len(self.turns) == 0:
            raise Exception("First turn, can not skip")
            
        cards_type = None
        if  not skip:
            if not player.has_cards(cards):
                raise Exception("player has not these cards")
        
            cards_type = self.rule.get_cards_type(cards)
            if cards_type == None:
                raise Exception("can not play it since wrong cards type")
        
            if len(self.turns) != 0: 
                last_cards_type  = None
                last_cards_player = None
                
                for turn in reversed(self.turns):
                    if not turn.skip:
                        last_cards_type = turn.cards_type 
                        last_player = turn.player    
                               
                
                if last_player != player and last_cards_type >= cards_type:
                    raise Exception("can not play it since cards is smaller than last one")
                    
                    
        
        player.remove_cards(cards)
        self.turns.append(PlayTurn(player,skip,cards,cards_type))

    
def test():
    l = Landlord(1,2,3)
    l.deal_bomb()
    print l.players[0]
    return l
        
if __name__ == '__main__':
    l = Landlord(1,2,3)
    l.deal_bomb()
    print l.players[0]
    print l.players[1]
    print l.players[2]  
    print l.leave_cards  
    
    cards = [Card(1,3),Card(2,3),Card(4,3),Card(3,3)]
    
    print "====>"
    rule = Rule()
    #for i in range(100000):
    print    rule.get_cards_type(cards)
