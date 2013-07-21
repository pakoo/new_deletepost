#/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.template
import tornado.httpserver
import logging
from BeautifulSoup import BeautifulSoup
import time
import pymongo
from pymongo import MongoClient
from pymongo import ASCENDING,DESCENDING
from datetime import datetime

con = MongoClient('localhost',27017)

goo = con.x


def get_all_item(page=1,count=50):
    return goo.item.find(skip=(page-1)*count,limit=50)

def get_all_keyword(category='',page=1,count=50):
    if category:
        return goo.keyword.find({'category':category},skip=(page-1)*count,limit=50)
    else:
        return goo.keyword.find(skip=(page-1)*count,limit=50)

def add_new_keyword(name,category='digit',weight=1):
    if not goo.keyword.find_one({'name':name}):
        print 'add new keyword "%s"'%name
        goo.keyword.insert({'name':name,'category':category,'createtime':datetime.now(),'weight':weight})


def get_all_shop(page=1,count=50):
    """
    """
    return goo.shop.find(skip=(page-1)*count,limit=50)

class heregoo(tornado.web.RequestHandler):

    def get(self,page):
        page = int(page)
        if page >0:
            self.render('manage.html',items=get_all_item(page),page=page)
        else:
            self.finish('fuck you')

class heregoo_keyword(tornado.web.RequestHandler):

    def get(self):
        #page = int(page)
        self.render('keyword.html',keywords=get_all_keyword('digit'),page=1)

class heregoo_shop(tornado.web.RequestHandler):

    def get(self,page):
        page = int(page)
        if page >0:
            self.render('shop.html',shops=get_all_shop(page),page=page)
        else:
            self.finish('fuck you')

class heregoo_add_keyword(tornado.web.RequestHandler):

    def post(self):
        #page = int(page)
        print 'category:',self.get_argument('category','')
        keyword = self.get_argument('keyword','')
        add_new_keyword(keyword)
        self.redirect('/keyword/')

class Application(tornado.web.Application):
    def __init__(self):
        app_settings={
            'debug':True,
        }
        handlers = [
            (r'/top/([0-9]+)/',heregoo),
            (r'/keyword/',heregoo_keyword),
            (r'/add_keyword',heregoo_add_keyword),
            (r'/shop/([0-9]+)/',heregoo_shop),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": "../static"}),
        ]
        tornado.web.Application.__init__(self,handlers,**app_settings)

if __name__ == '__main__':
    pass
    http_server = tornado.httpserver.HTTPServer(request_callback=Application())
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

    #print get_all_item()[0]
    #add_new_keyword('macbook air')
    #print get_all_keyword()
