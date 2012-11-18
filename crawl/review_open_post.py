#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Author:pako
#Email:zealzpc@gmail.com
"""
some db interface 
"""
import pymongo
import pycurl
import StringIO
import time
from BeautifulSoup import BeautifulSoup
import os
import traceback
import datetime
import gridfs
from kds import get_tieba_reply
from smallgfw import GFW
import os
mktime=lambda dt:time.mktime(dt.utctimetuple())
######################db.init######################
con = pymongo.Connection('localhost', 27017)
kds=con.kds
######################db.init######################
gfw = GFW()
gfw.set(open(os.path.join('keyword.txt')).read().split('\n'))

def get_html(url):
    print 'url:',url
    html=''
    try:
        crl = pycurl.Curl()
        crl.setopt(pycurl.VERBOSE,1)
        crl.setopt(pycurl.FOLLOWLOCATION, 1)
        crl.setopt(pycurl.MAXREDIRS, 5)
        crl.setopt(pycurl.CONNECTTIMEOUT, 5)
        crl.setopt(pycurl.TIMEOUT, 30)
        crl.fp = StringIO.StringIO()
        crl.setopt(pycurl.URL, url)
        crl.setopt(crl.WRITEFUNCTION, crl.fp.write)
        crl.perform()
        html=crl.fp.getvalue()
        crl.close()
    except Exception,e:
        print('\n'*9)
        traceback.print_exc()
        print('\n'*9)
        return None
    return html

def update_post(url,db,content=None,is_open=1):
    if is_open ==0 :
        con[db].post.update({'url':url},{'$set':{'is_open':is_open,'find_time':time.time()}})
    else:
        con[db].post.update({'url':url},{'$set':{'is_open':is_open,'find_time':time.time()}})
        

def kds_review():
    db = con['kds']
    yesterdat=time.time()-48*3600
    #yesterdat=time.time()-100
    old_post=db.post.find({'create_time':{'$lt':yesterdat},'is_open':1})
    #old_post=db.post.find({'is_open':1})
    #old_post=post.find({'is_open':1})
    print 'old post amount:',old_post.count()
    root="http://club.pchome.net/" #root = "http://tieba.baidu.com/p/" try:
    try:
        for tiezi in old_post:
                post_url=str(os.path.join(root,str(tiezi['url'])))  
                post_html=get_html(post_url)
                if post_html is None:
                    continue
                #post_soup = BeautifulSoup(post_content_all,fromEncoding='gbk')
                #post_content=post_soup.find('div',{'class':'mc'})
                if 'backHome' in post_html:
                    print '>>>>>>>>>>>>>>>>find a delete post!<<<<<<<<<<<<<<<<<<<<'
                    print '>>>>>>>>>>>>>>>>%s<<<<<<<<<<<<<<<<<<<<'%post_url
                    update_post(url = tiezi['url'],db='kds',is_open=0)   
                else:
                    print '>>>>>>>>>>>>>>>>删除了已经存在了48h的帖子%s !<<<<<<<<<<<<<<<<<<<<'%tiezi['url']
                    db.post.remove({'url':tiezi['url']}) 
    except Exception,e:
        traceback.print_exc() 
        pass

def tieba_review(dbname):
    db = con[dbname]
    #yesterdat=time.time()-48*3600
    yesterdat=time.time()-100
    old_post=db.post.find({'create_time':{'$lt':yesterdat},'is_open':1,'tieba_name':'liyi'})
    #old_post=con[dbname].post.find({'is_open':1})
    print 'old post amount:',old_post.count()
    root = "http://tieba.baidu.com/p/"
    try:
        for tiezi in old_post:
                post_url=os.path.join(root,str(tiezi['url']))  
                post_content_all=get_html(post_url)
                if not post_content_all:
                    continue
                if 'closeWindow' in post_content_all :
                    print '>>>>>>>>>>>>>>>>find a delete post!<<<<<<<<<<<<<<<<<<<<'
                    print '>>>>>>>>>>>>>>>>%s<<<<<<<<<<<<<<<<<<<<'%post_url
                    org_title= tiezi['title'].encode('utf-8')
                    filter_title = gfw.replace(org_title)
                    if filter_title != tiezi['title']:
                        update_post(url = tiezi['url'],db='tieba',is_open=-1)
                    else:
                        update_post(url = tiezi['url'],db='tieba',is_open=0)   
                else:
                    print '>>>>>>>>>>>>>>>>删除了已经存在了48h的帖子%s !<<<<<<<<<<<<<<<<<<<<'%tiezi['url']
                    con['tieba'].post.remove({'url':tiezi['url']}) 
                        
    except Exception,e:
        traceback.print_exc() 
        pass
if __name__ == "__main__":
    while True:
        try:
            tieba_review('tieba')
            kds_review()
            time.sleep(600)
        except Exception,e:
            print('\n'*9)
            traceback.print_exc()
            print('\n'*9)
    #print tieba_review('tieba')

    #update_post({'url':"thread_1_15_6890043__.html",'is_open':0})
