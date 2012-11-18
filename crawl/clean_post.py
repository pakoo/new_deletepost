#! /usr/bin/env python
# -*- coding: utf-8 -*-
#Author:pako
#Email:zealzpc@gmail.com
"""
some db interface
"""
import pymongo
import time
import traceback
import datetime
import kds
import os
mktime=lambda dt:time.mktime(dt.utctimetuple())
######################db.init######################
con = pymongo.Connection('localhost', 27017)
db=con.tieba
post=db.post

######################db.init######################
#yesterdat=time.time()-35*3600
close_post=post.find({'is_open':1})
print 'old post amount:',close_post.count()
root = "http://tieba.baidu.com/p/"
if close_post.count() >0:
    for cpost in close_post:
        post_url=os.path.join(root,str(cpost['url']))
        html = kds.get_html(post_url)
        print 'post url:',post_url
        if html is None:
            continue
        if 'closeWindow' not in html :
            print '>>>>>>>>>>>>>>>>发现一个被误认未删除的帖子，现在将其删除!<<<<<<<<<<<<<<<<<<<<'
            print '>>>>>>>>>>>>>>>>%s<<<<<<<<<<<<<<<<<<<<'%post_url
            post.remove({'url':cpost['url']})
        else:
            print '>>>>>>>>>>>>>>>>验证了是一个已经被删除的帖子 !<<<<<<<<<<<<<<<<<<<<'

