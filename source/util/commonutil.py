#coding: utf-8

import logging
import traceback
import time
import random


def choice_dist_mode(lst,prob_key):
	total = reduce(lambda x,y: x + prob_key(y),lst,0)
	prob = random.randint(0,total)
	for item in lst:
		item_prob = prob_key(item)
		if item_prob >= prob:
			return item
		prob -= item_prob
	return None
	
class CollectionsUtil:
    @staticmethod
    def filter_one(lst,value,min_key,max_key):
        if callable(min_key):
            tmp = filter(lambda x:max_key(x) > value >= min_key(x),lst)
        else:
            tmp = filter(lambda x:getattr(x,max_key) > value >= getattr(x,min_key),lst)
        if len(tmp) == 0:
            return None
        return tmp[0]
    
        
        
    	