#-*- coding: utf-8 -*- 
import logging
from datetime import datetime, date
import traceback
import gredis
import  settings
from cacheKey import game_log_list

def write_log(module, type, avatar_id, attr, num, reason):
    """
    记录一些非玩家属性变化的日志
    如完成副本次数等
    """
    try:
        log_list = gredis.get_list(game_log_list)
        today = date.today()
        today_str = ''.join(str(today).split('-'))
        log_temp = '%s %s %s %s %s %s %s\n'%(datetime.now(), module, type,
                avatar_id, attr, num, reason)
        logging.info('log_temp:%s'%log_temp)
        log_list.push(log_temp)
    except Exception ,e:
        logging.error(traceback.format_exc())
