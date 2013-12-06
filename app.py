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
import requests

con = MongoClient('localhost',27017)

db = con.air.pm
goo = con.x

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

news_tmp = """
<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <Content><![CDATA[]]></Content>
    <ArticleCount>%s</ArticleCount>
    <Articles>
    %s
    </Articles>
</xml> 
           """

item_tmp = """
    <item>
        <Title><![CDATA[%s]]></Title>
        <Description><![CDATA[%s]]></Description>
        <PicUrl><![CDATA[%s]]></PicUrl>
        <Url><![CDATA[%s]]></Url>
    </item>
           """

air_tmp = """
<html>
<title>test</title>
<body>
<p><a href="weixin://profile/gh_6d72fcf71ac6">美领馆PM2.5查询</a></p>
<p><img src="http://www.semc.gov.cn/aqi/home/images/landscape.jpg"></p>
</body>
</html>
"""

def get_pm(place):
    res = db.find_one({'location':place},sort=[('create_time',DESCENDING)])    
    if res:
        return res

def get_level(data):
    if 0<= data <=50:
        return "空气状况:优"
    elif 51<= data <=100: 
        return "空气状况:良"
    elif 101<= data <=150: 
        return "空气状况:轻度污染,建议佩戴口罩"
    elif 151<= data <=200: 
        return "空气状况:中度污染,建议佩戴口罩"
    elif 201<= data <=300: 
        return "空气状况:重度污染,建议不外出"
    else:
        return "空气状况:严重污染,建议不外出"

def update_menu():
    """
    更新菜单
    """
    menu = {
        "button":[
                    { 
                    #"type":"click",
                    "name":"城市",
                    "sub_button":[
                                {
                                "type":"click",
                                "name":"上海",
                                "key":"shanghai"
                                },
                                {
                                "type":"click",
                                "name":"北京",
                                "key":"beijing"
                                },
                                {
                                "type":"click",
                                "name":"广州",
                                "key":"guangzhou"
                                },
                                {
                                "type":"click",
                                "name":"成都",
                                "key":"chengdu"
                                },
                                ]
                    },

                    {
                    "type":"view",
                    "name":"官网",
                    "url":"http://www.oucena.com/"
                    },

                ]
    }


class weixin(tornado.web.RequestHandler):

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
        #items = [('title1','description1','http://oucena.com/static/img/bt.jpg','http://oucena.com/')]  
        #items_str = '\n'.join([item_tmp%i for i in items])
        #logging.info(items_str)
        #res = news_tmp%('asd','sdf',1287324,len(items),items_str) 
        #self.finish(res)

    def post(self):
        if self.msgtype == 'text':
            if self.wxtext in ('1','shanghai','上海') :
                res = get_pm('shanghai')
                pm25 = res['data']
                ctime = str(res['publish_time'])
                place = '上海'
            elif self.wxtext in ('2','北京','beijing'):
                res = get_pm('beijing')
                pm25 = res['data']
                ctime = str(res['publish_time'])
                place = '北京'
            elif self.wxtext in ('3','广州','guangzhou'):
                res = get_pm('guangzhou')
                pm25 = res['data']
                ctime = str(res['publish_time'])
                place = '广州'
            elif self.wxtext in ('4','成都','chengdu'):
                res = get_pm('chengdu')
                pm25 = res['data']
                ctime = str(res['publish_time'])
                place = '成都'
            elif self.wxtext == '5':
                items = [('title1','description1','http://oucena.com/static/img/bt.jpg','http://oucena.com/airpic')]  
                self.send_news(items)
            else:
                a = """发送 “1”查询上海 美国领事馆发布的 pm2.5 数据
                     \n发送 “2”查询北京 美国领事馆发布的 pm2.5 数据
                     \n发送 “3”查询广州 美国领事馆发布的 pm2.5 数据
                     \n发送 “4”查询成都 美国领事馆发布的 pm2.5 数据
                    """
                self.send_text(a)    
                return 
            air_level =get_level(int(float(pm25)))  
            msg = "%s %s PM2.5:%s  %s "%(ctime,place,pm25,air_level)
            if self.wxtext =="1":
                self.send_air_pic(pm25,msg)
            else:
                self.send_text(msg)    
        elif self.msgtype == 'location':
            self.send_text('我收到你消息啦!!')
        elif self.msgtype == 'image':
            self.send_text('我收到你消息啦!!')

    def send_text(self,msg):
        #self.set_header("Content-Type","application/xml; charset=UTF-8")
        line = text_tmp%(self.userid,self.myid,int(time.time()),msg) 
        self.finish(line)

    def send_news(self,items):
        """
        发送图文
        """
        items_str = '\n'.join([item_tmp%i for i in items])
        logging.info(items_str)
        res = news_tmp%(self.userid,self.myid,int(time.time()),len(items),items_str) 
        self.finish(res)

    def send_air_pic(self,pm25,msg):
        pic_url = self.get_shanghai_air_pic()
        items = [('上海PM2.5浓度为:%s'%pm25,msg,pic_url,pic_url)]  
        self.send_news(items)

    def get_shanghai_air_pic(self):
        n = datetime.now()
        if n.month < 10:
            month = "0%s"%n.month
        else:
            month = n.month
        if n.day < 10:
            day = "0%s"%n.day
        else:
            day = n.day
        if n.hour < 10:
            hour = "0%s"%(n.hour-1)
        else:
            hour = n.hour-1
        url = "http://www.semc.gov.cn/aqi/home/images/pic/%s%s%s%s00.jpg"%(n.year,month,day,hour)
        #print 'shanghai air pic:',url
        #return url
        return "http://www.semc.gov.cn/aqi/home/images/landscape.jpg"
        
        
class AirPic(tornado.web.RequestHandler):

    def get(self):
        self.finish(air_imp)
            
class towww(tornado.web.RequestHandler):

    def get(self):
        uri = self.uri     
        print 'uri:',self.uri
        self.finish(self.uri)
        #self.redirect('www.404cn.org'+slef.uri, permanent=True)

class tufuli(tornado.web.RequestHandler):

    def get(self):
        self.finish('b97ac2b5f862000c013621616f783a78')
        #self.redirect('www.404cn.org'+slef.uri, permanent=True)
        
class www(tornado.web.RequestHandler):

    def get(self):
        #loader = tornado.template.Loader("./tufuli/")
        #self.finish(loader.load('base.html').generate({}))
        self.render('tufuli/base.html',mainpage='active')


class Application(tornado.web.Application):
    def __init__(self):
        app_settings={
            'debug':True,
        }
        handlers = [
            (r'/',weixin),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": "./static"}),
        ]
        tornado.web.Application.__init__(self,handlers,**app_settings)

if __name__ == '__main__':
    pass
    http_server = tornado.httpserver.HTTPServer(request_callback=Application())
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()

    #print get_all_item()[0]
    #add_new_keyword('macbook air')
    #print get_all_keyword()
