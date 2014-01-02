#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Author:pako
#Email:zealzpc@gmail.com
"""
some db interface 
"""
import pymongo
from pymongo import ASCENDING,DESCENDING
from bson.objectid import ObjectId as monid
import gridfs
import time
import os
from hashlib import md5
mktime=lambda dt:time.mktime(dt.utctimetuple())
######################db.init######################
#con = pymongo.Connection('199.15.113.215', 27017)
con = pymongo.Connection('localhost', 27017)
kds=con.kds
tieba=con.tieba
db_web = con.web
#db_post=kds.post
#db_fs=gridfs.GridFS(kds,'postfile')
debug_flag = 0
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
    delete_post_list=tieba.post.find({'is_open':debug_flag,'tieba_name':'liyi'},{'url':1,'title':1,'find_time':1,'user_name':1,'click':1,'is_liang':1},limit=count,skip=count*(page-1),sort=[('find_time',DESCENDING)])
    #print 'delete_post_list:',delete_post_list
    #print 'delete_post_amount:',delete_post_list.count()
    if delete_post_list.count()>0:
        item_num=0
        for p in delete_post_list:
            #print 'post:',p['url']
            result.append([
                          "/tieba/post/%s"%p['url'],
                          p['title'],
                          transUinxtime2Strtime(p['find_time']),
                          p['user_name'],
                          item_num,
                          p['click'],
                          p.get('is_liang',0),
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
                                  },{'url':1,'title':1,'find_time':1,'user_name':1,'click':1,'is_liang':1},limit=count,skip=count*(page-1),sort=[('last_click_time',DESCENDING)])
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

def get_filter_post_url(page,count=50):
    """
    获取被和谐过的帖子列表 
    """
    now = int(time.time())
    result=[]
    hot_post = get_hot_post('tieba')
    hot_post_list=tieba.post.find({'is_open':-9},limit=count,skip=count*(page-1),sort=[('create_time',DESCENDING)])
    if hot_post_list.count()>0:
        item_num=0
        for p in hot_post_list:
            print 'post:',p['url']
            result.append([
                          "/fuli/%s"%p['url'],
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

def get_tieba_post_reply(url,dbname,is_open=0):
    """
    获取帖子的内容
    """
    if dbname == 'tieba':
        tieba_url_root = "http://tieba.baidu.com/p"
    elif dbname == 'kds':
        tieba_url_root = "http://club.pchome.net"

    db_reply = con[dbname].post
    res = db_reply.find_one({'url':url,'is_open':is_open})
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
            if res.get('user_reply',None):
                for reply in res['user_reply']:
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


def hide_post(post_url,dbname):
    """
    hide post
    """
    print 'dbname:',dbname
    db_post = con[dbname].post
    db_ban_user = con[dbname].ban_user
    if dbname == 'tieba':
        post=db_post.update({'url':int(post_url)},{'$set':{'is_open':-9}})
    elif dbname == 'kds':
        post=db_post.update({'url':post_url},{'$set':{'is_open':-9}})
    return 1

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

def create_user(name,password,ip='',email=''):
    """
    创建用户
    """
    if name and password:
        print 'name:',name
        print 'password:',password
    else:
        return 0
    user_name_check = db_web.user.find_one({'name':name}) 
    if not user_name_check :
        #用户名不存在，创建新用户
        m = md5()
        m.update(password)
        user = {'name':name,
                'password':m.hexdigest(),
                'email':email,
                'is_master':0,
                'ip':ip,
        }
        db_web.user.insert(user)
        print "%s注册成功!!"%name
        return 1
    else:
        #用户名已存在
        return -1

def user_login(name,password):
    """
    用户登录
    """
    if name and password:
        print 'name:',name
        print 'password:',password
        m = md5()
        m.update(password)
        password_md5 =m.hexdigest()
    else:
        return 0

    user_name_pwd_check = db_web.user.find_one({'name':name,'password':password_md5}) 

    if user_name_pwd_check:
        #用户名密码正确
        return 1
    else:
        #用户名密码错误k
        return -1

def add_advice(content,name='',ip=''):
    """
    添加留言
    """
    print 'content:',content
    print 'name:',name
    if len(content) > 140:
        print "留言太长!!!"
    else:
        advice = {
                 'content':content,
                 'name':name,
                 'ip':ip,
                 'create_time':int(time.time()),
        }
        db_web.advice.insert(advice)

def get_advice():
    """
    获取留言
    """
    advice_list = db_web.advice.find({},limit=20,skip=0,sort=[('create_time',DESCENDING)])
    advice_list = [(a['name'],a['content']) for a in advice_list if a['content']]
    print 'advice_list:',advice_list
    return advice_list 
    
def get_tu(page=1,bar_name='jietup',count=24):
    """
    获取图吧图片
    """
    img_url_list = con['tieba'].img.find({'type_name':bar_name,'is_open':1},limit=count,skip=(page-1)*count,sort=[('last_click_time',DESCENDING)])
    if img_url_list.count()>0:
        return img_url_list


def add_new_reply(url,content):
    """
    添加一条新评论
    """
    con['tieba'].post.update({'url':url},{'$push':{'user_reply':content}})

def exist_post(url):
    """
    是否存在这个帖子
    """
    if con['tieba'].post.find_one({'url':int(url)}):
        return True

def delete_tu(url):
    """
    删除图片
    """
    con['tieba'].img.update({'url':url},{'$set':{'is_open':-1}})

def hide_tu(url):
    """
    隐藏图片
    """
    con['tieba'].img.update({'url':url},{'$set':{'is_open':9}})
    

if __name__ == "__main__":
    pass
    #print get_delete_post_url()
    #print get_tieba_delete_post_url()
    #print get_post_html(1584957558,'tieba')
    #print delete_post(1584957558,db=tieba)
    #print get_tieba_post_reply(1599791533,'tieba')
    #print get_hot_post('tieba')
    #print create_user('oucena','zxzxzx','')
    #print user_login('gan','123456')
    #add_advice('test','admin')
    #print get_advice()
    #get_tu()
    delete_tu('52c564201d41c87a14000000')
