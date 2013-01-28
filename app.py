#/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.httpserver
import logging
from BeautifulSoup import BeautifulSoup
import time
import pymongo
from pymongo import MongoClient
from pymongo import ASCENDING,DESCENDING

con = MongoClient('localhost',27017)
db = con.air.pm

text_tmp = """
<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    <FuncFlag>0</FuncFlag>
</xml> 
            """

def get_pm(place):
    res = db.find_one({'location':place},sort=[('create_time',DESCENDING)])    
    if res:
        return res

class  weixin(tornado.web.RequestHandler):

    def prepare(self):
        print '\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        print 'body:',self.request
        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        if self.request.method == 'POST':
            soup = BeautifulSoup(self.request.body)
            self.userid  = soup.find('fromusername').text
            self.createtime = soup.find('createtime').text
            self.msgtype = soup.find('msgtype').text
            self.myid = soup.find('tousername').text
            if self.msgtype == 'text':
                self.wxtext = soup.find('content').text
                print 'text:',self.wxtext  
            elif self.msgtype == 'location':
                self.location_x = soup.find('location_x').text 
                self.location_y = soup.find('location_y').text 
                self.location_scale = soup.find('scale').text 
                self.location_lable = soup.find('label').text 
                print 'x:',self.location_x  
                print 'y:',self.location_y
            elif self.msgtype == 'image':
                self.picurl = soup.find('picurl').text 
                print 'pic url:',self.picurl 
        else:
            logging.info('request:%s'%self.request) 

    def get(self):
        logging.info('arguments:%s'%str(self.get_arguments('echostr','')))
        print 'echostr:',self.get_arguments('echostr','')
        self.finish(self.get_argument('echostr',''))

    def post(self):
        if self.msgtype == 'text':
            if self.wxtext == '1':
                res = get_pm('shanghai')
                pm25 = res['data']
                ctime = str(res['publish_time'])
                place = '上海'
            elif self.wxtext == '2':
                res = get_pm('beijing')
                pm25 = res['data']
                ctime = str(res['publish_time'])
                place = '北京'
            elif self.wxtext == '3':
                res = get_pm('guangzhou')
                pm25 = res['data']
                ctime = str(res['publish_time'])
                place = '广州'
            elif self.wxtext == '4':
                res = get_pm('chengdu')
                pm25 = res['data']
                ctime = str(res['publish_time'])
                place = '成都'
            else:
                a = """发送 “1”查询上海 美国领事馆发布的 pm2.5 数据
                     \n发送 “2”查询北京 美国领事馆发布的 pm2.5 数据
                     \n发送 “3”查询广州 美国领事馆发布的 pm2.5 数据
                     \n发送 “4”查询成都 美国领事馆发布的 pm2.5 数据
                    """
                self.send_text(a)    
                return 
                
            self.send_text("%s %s PM2.5:%s   "%(ctime,place,pm25))    
        elif self.msgtype == 'location':
            self.send_text('我收到你消息啦!!')
        elif self.msgtype == 'image':
            self.send_text('我收到你消息啦!!')

    def send_text(self,msg):
        #self.set_header("Content-Type","application/xml; charset=UTF-8")
        line = text_tmp%(self.userid,self.myid,int(time.time()),msg) 
        self.finish(line)
            
class Application(tornado.web.Application):
    def __init__(self):
        app_settings={
            'debug':True,
        }
        handlers = [
            (r'/',weixin),
        ]
        tornado.web.Application.__init__(self,handlers,**app_settings)

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(request_callback=Application())
    http_server.listen(7070)
    tornado.ioloop.IOLoop.instance().start()
