#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Author:pako
#Email:zealzpc@gmail.com
"""
some db interface 
"""
import pymongo
from pymongo import ASCENDING,DESCENDING
import gridfs
import time
import os
mktime=lambda dt:time.mktime(dt.utctimetuple())
######################db.init######################
con = pymongo.Connection('199.15.113.215', 27017)
kds=con.kds
tieba=con.tieba
#db_post=kds.post
#db_fs=gridfs.GridFS(kds,'postfile')
debug_flag = 1
######################db.init######################
def transUinxtime2Strtime(utime,type=0):
#    stime=time.strftime("%a, %d %b",time.localtime(utime))
    if type==0:
        stime=time.strftime("%Y-%m-%d %H:%M",time.localtime(utime))
        return stime
    elif type==1:
        stime=time.strftime("%m.%d",time.localtime(utime))
        return stime


def get_hot_post(dbname):
    """
    获取点击数最高的10篇帖子
    """
    db = con[dbname]
    db_post = db.post

    now = int(time.time())
    top10 = db_post.find({'is_open':debug_flag,
                                   'last_click_time':{'$lt':now,'$gt':now-24*3600}
                                  },limit=10,sort=[('last_click_time',DESCENDING)])
    #top10 = db_post.find({'is_open':debug_flag},limit=10,sort=[('click',DESCENDING)])

    hot_post = []
    for tie in top10:
        print 'id:',tie['url'],'   click:',tie.get('click',0)
        if dbname =='tieba':
            url = "/tieba/post/%s"%tie['url']
        else:
            url = "/kds/post/%s"%tie['url']
        hot_post.append(
                        (url,
                        tie['title']
                        )
        )
    return hot_post

def get_delete_post_url(page,count=50):
    result=[]
#    delete_post_list=db_post.find()
    delete_post_list=kds.post.find({'is_open':debug_flag},limit=count,skip=count*(page-1),sort=[('create_time',DESCENDING)])
    print 'delete_post_list:',delete_post_list
    if delete_post_list.count()>0:
        item_num=0
        for p in delete_post_list:
            result.append([
                          "/kds/post/%s"%p['url'],
                          p['title'],
                          transUinxtime2Strtime(p['create_time']),
                          p['user_name'],
                          item_num,
                          ]
                          )
            item_num+=1
        return result,kds.post.count()
    else:
        return None

def get_tieba_delete_post_url(page,count=50):
    print 'a'
    result=[]
    hot_post = get_hot_post('tieba')
    delete_post_list=tieba.post.find({'is_open':debug_flag,'tieba_name':'liyi'},limit=count,skip=count*(page-1),sort=[('find_time',DESCENDING)])
    #print 'delete_post_list:',delete_post_list
    #print 'delete_post_amount:',delete_post_list.count()
    if delete_post_list.count()>0:
        item_num=0
        for p in delete_post_list:
            print 'post:',p['url']
            result.append([
                          "/tieba/post/%s"%p['url'],
                          p['title'],
                          transUinxtime2Strtime(p['find_time']),
                          p['user_name'],
                          item_num,
                          p['click'],
                          ]
                          )
            item_num+=1
        return result,hot_post,tieba.post.count()
    else:
        return None

def get_tieba_today_hot_post_url(page,count=50):
    """
    获取24小时内被点击过的帖子
    """
    now = int(time.time())
    result=[]
    hot_post = get_hot_post('tieba')
    hot_post_list=tieba.post.find({'is_open':debug_flag,
                                   'last_click_time':{'$lt':now,'$gt':now-24*3600}
                                  },limit=count,skip=count*(page-1),sort=[('last_click_time',DESCENDING)])
    #print 'hot_post_list:',hot_post_list
    #print 'hot_post_amount:',hot_post_list.count()
    if hot_post_list.count()>0:
        item_num=0
        for p in hot_post_list:
            print 'post:',p['url']
            result.append([
                          "/tieba/post/%s"%p['url'],
                          p['title'],
                          transUinxtime2Strtime(p['find_time']),
                          p['user_name'],
                          item_num,
                          p['click'],
                          ]
                          )
            item_num+=1
        return result,hot_post,tieba.post.count()
    else:
        return None

def get_tieba_post_reply(url,dbname):
    """
    获取帖子的回复信息
    """
    if dbname == 'tieba':
        tieba_url_root = "http://tieba.baidu.com/p"
    elif dbname == 'kds':
        tieba_url_root = "http://club.pchome.net"

    db_reply = con[dbname].post
    res = db_reply.find_one({'url':url})
    if res:
        db_reply.update({'url':url},{'$inc':{'click':1}})
        db_reply.update({'url':url},{'$set':{'last_click_time':int(time.time())}})
        res['original_url'] = os.path.join(tieba_url_root,str(url))
        if res['content']:
            fcount = 1
            for reply in res['content']:
                #print 'reply:',reply
                if dbname == 'tieba':
                    reply['create_time'] = transUinxtime2Strtime(reply['create_time'])
                reply['floor'] = fcount
                fcount +=1
        return res
    

def delete_post(post_url,dbname):
    """
    delete post
    """
    print 'dbname:',dbname
    db_post = con[dbname].post
    db_ban_user = con[dbname].ban_user
    if dbname == 'tieba':
        post=db_post.find_one({'url':int(post_url)})
    elif dbname == 'kds':
        post=db_post.find_one({'url':post_url})
    print 'post:',post
    if post:
        db_post.remove(post['_id'])
        ban_user_check = db_ban_user.find_one({'user_name':post['user_name']})
        #print 'ban_user_check:',ban_user_check
        if ban_user_check is None:
            db_ban_user.insert({'user_name':post['user_name']})
        else:
            print "%s已经再黑名单中"%post['user_name']
        return  'success!'
    else:
        return 'a wrong url,not exist this post to delete!'

def search_post(keyword='',page=1,tieba_name='liyi'):
    """
    根据帖子标题搜索帖子
    """
    if keyword:
        db_post = con.tieba.post
        search_res = db_post.find({'title':{'$regex':'.%s.'%keyword}},limit=50,skip=50*(page-1),sort=[('find_time',DESCENDING)])
        result = []
        if search_res.count()>0:
            hot_post = get_hot_post('tieba')
            item_num=0
            for p in search_res:
                print 'post:',p['url']
                result.append([
                              "/tieba/post/%s"%p['url'],
                              p['title'],
                              transUinxtime2Strtime(p['find_time']),
                              p['user_name'],
                              item_num,
                              p['click'],
                              ]
                              )
                item_num+=1
            return result,hot_post,tieba.post.count()

if __name__ == "__main__":
    #print get_delete_post_url()
    #print get_tieba_delete_post_url()
    #print get_post_html(1584957558,'tieba')
    #print delete_post(1584957558,db=tieba)
    #print get_tieba_post_reply(1599791533,'tieba')
    print get_hot_post('tieba')
