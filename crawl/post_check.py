#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Author:pako
#Email:zealzpc@gmail.com
"""
some db interface 
"""
import pymongo
import pycurl
from BeautifulSoup import BeautifulSoup 
import StringIO
import time
from django.utils.encoding import smart_str, smart_unicode
import os
import traceback
import datetime
import gridfs
mktime=lambda dt:time.mktime(dt.utctimetuple())
######################db.init######################
connection = pymongo.Connection('localhost', 27017)
db=connection.kds
post=db.post
fs=gridfs.GridFS(db,'postfile')
######################db.init######################
root="http://club.pchome.net/"
mainurl="http://club.pchome.net/forum_1_15.html"
    
    
def transUinxtime2Strtime(utime,type=0):
#    stime=time.strftime("%a, %d %b",time.localtime(utime))
    if type==0:
        stime=time.strftime("%Y-%m-%d %H:%S",time.localtime(utime))
        return stime
    elif type==1:
        stime=time.strftime("%m.%d",time.localtime(utime))
        return stime

def get_html(url):
    html=''
    try:
        crl = pycurl.Curl()
        crl.setopt(pycurl.VERBOSE,1)
        crl.setopt(pycurl.FOLLOWLOCATION, 1)
        crl.setopt(pycurl.MAXREDIRS, 5)
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

def update_open(url,is_open):
    post.update({'url':url},{'$set':{'is_open':is_open,
                                         }})
print 'totle post amount:',post.count()
print '='*50
print '='*50
delete_post=post.find({'is_open':0})
if delete_post.count() >0 :
    print 'totle delete post amount:',delete_post.count()
    for p in delete_post:
        print 'create_time:',transUinxtime2Strtime(p['create_time'])
        print 'url:',p['url']
#        print 'title:',p['title']
    print '='*50
    print '='*50
    delete_post=post.find({'is_open':0}) 
    for p in delete_post:
        post_url=str(os.path.join(root,p['url']))
        post_content=get_html(post_url)
        if not post_content:
            continue
        post_soup = BeautifulSoup(post_content,fromEncoding='gbk')
        post_content=post_soup.find('div',{'class':'mc'})
        if post_content:
            print 'url(%s) is wrong kill'%p['url']
            update_open(p['url'],1)
        
