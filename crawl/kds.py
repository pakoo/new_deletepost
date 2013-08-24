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
import simplejson as json
import types
from smallgfw import GFW
import os 
import os.path
from pymongo import ASCENDING,DESCENDING
import requests
from urlparse import urlparse
import sys
mktime=lambda dt:time.mktime(dt.utctimetuple())
######################db.init######################
connection = pymongo.Connection('localhost', 27017)

kds=connection.kds
post=kds.post
kdsuser=kds.user
#fs=gridfs.GridFS(kds,'postfile')

tieba = connection.tieba
tieba_post = tieba.post
tieba_user = tieba.user

browser = requests.session()
######################gfw.init######################
gfw = GFW()
gfw.set(open(os.path.join(os.path.dirname(__file__),'keyword.txt')).read().split('\n'))

lgfw = GFW()
lgfw.set(['thunder://','magnet:','ed2k://'])



tongji = """
<center>
<script language="javascript" type="text/javascript" src="http://js.users.51.la/5988086.js"></script>
<noscript><a href="http://www.51.la/?5988086" target="_blank">
<img alt="&#x6211;&#x8981;&#x5566;&#x514D;&#x8D39;&#x7EDF;&#x8BA1;" src="http://img.users.51.la/5988086.asp" style="border:none" /></a>
</noscript>
</center>
"""
#def save_post(url,html,db=None):
#    """
#    save post html
#    """
#    print 'db:',db
#    print 'post:',db.post
#    res=db.post.find_one({'url':url})
#    html = html+tongji
#    fs=gridfs.GridFS(db,'postfile')
#    if res:
#        print 'find exist post!'
#        old_fid=res['fid']
#        if old_fid:
#            print 'find old_fid:',old_fid
#            fs.delete(old_fid)
#        #print 'post html len:',len(html)
#        new_fid=fs.put(html)
#        db.post.update({'url':url},{'$set':{'fid':new_fid,
#                                         }})
#    else:
#        new_fid=fs.put(html)
#    return new_fid     

def save_user(user_id,user_name,dbname=None):
    db = connection[dbname] 
    res=db.user.find_one({'user_name':user_name})
    if res:
        db.user.update({'user_id':user_id},{'$inc':{'post_count':1}})
    else:
        db.user.insert({'user_id':user_id,'user_name':user_name,'post_count':1})

def get_html(url):
    print '============================================'
    print 'url:',url
    print '============================================'
    time.sleep(1)
    html=''
    try:
        crl = pycurl.Curl()
        crl.setopt(pycurl.VERBOSE,1)
        crl.setopt(pycurl.FOLLOWLOCATION, 1)
        crl.setopt(pycurl.MAXREDIRS, 5)
        crl.setopt(pycurl.CONNECTTIMEOUT, 8)
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

    #r = requests.get(url)
    #return r.text

    #r = browser.get(url)
    #return r.content

def get_tieba_mainpage(url):
    """
    获取百度贴吧首页
    """

def post_insert(para,dbname=None):
    db = connection[dbname] 
    db_ban_user = db.ban_user
    #print 'insert data:',para
#    print para.keys()
#    print 'user_id:',para['user_id']
    print 'is_open:',para['is_open']
    url=para['url']
    res=db.post.find_one({'url':url})
    #save_user(para['user_id'],para['user_name'],dbname=dbname)
    #ban_user_check = db_ban_user.find_one({'user_name':para['user_name']})
    #print 'ban_user_check:',ban_user_check
    #if ban_user_check is not None:
    #    print "发现一个黑名单用户%s的帖子"%para['user_name']
    #    para['is_open'] = 2

    #org_title = para['title'].encode('utf-8')
    #filter_title = gfw.replace(org_title)
    #过滤不和谐帖子
    #if filter_title != org_title:
    #    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>发现不和谐帖子<<<<<<<<<<<<<<<<<<<<<<<<<<'
    #    para['is_open']=-1
    if res:
        if para['is_open'] == 0:
            print "发现了一个被删掉的帖子 %s"%para['url']
            db.post.update({'url':url},{'$set':{'reply':para['reply'],
                                             'is_open':para['is_open'],
                                             'find_time':para['find_time'],
                                             }})
        else:
            print "发现了一个已经存在的帖子 但没被删除 更新其内容 %s"%para['url']
            db.post.update({'url':url},{'$set':{'reply':para['reply'],
                                             'is_open':para['is_open'],
                                             'content':para['content'],
                                             }})
            
        print 'this %s post have existed !'%url
    elif para['content']:     
        db.post.insert(para)
        print 'insert data success!!'

    print '='*50+'\n\n'

def reply_img_insert(db_name='tieba',sort_name='liyi',img_url='',post_url=''):
    """
    存储图片
    """
    url = os.path.split(img_url)[-1]
    db = connection[db_name] 
    db_img = db.img
    img_is_exist = db_img.find_one({'url':url})
    img_info = {
                'type_name':sort_name,
                'url':url,
                'post_url':post_url,
                'create_time':int(time.time()),
                'last_click_time':int(time.time()),
                'click':0,
                'is_open':1,
    }
    if url and img_is_exist is None:
        print ">>>>>>>>>>>>>>>>>>>>发现一张(%s)新图 %s，插入了数据库<<<<<<<<<<<<<<<<<<"%(db_name,url)
        db_img.insert(img_info)


def transtime(stime):
    """
            将'11-12-13 11:30'类型的时间转换成unixtime
    """
    if stime and ':' in stime:
        res=stime.split(' ')
        year,mon,day=[int(i) for i in res[0].split('-')]
        hour,second=[int(i) for i in res[1].split(':')]
        unixtime=mktime(datetime.datetime(year,mon,day,hour,second))
        return unixtime
    else:
        return int(time.time())
    
def get_kds_post():
    root="http://club.pchome.net/"
    mainurl="http://club.pchome.net/forum_1_15.html"
    html=get_html(mainurl)
    if html:
        soup = BeautifulSoup(html,fromEncoding='gbk')
        #soup = BeautifulSoup(html)
        posts=soup.findAll('li',{'class':'i2'})
        #print 'post:',posts
        for p in posts:
            p_li=p.findAll('span')
            p_a=p.findAll('a')
            for a in  p_li:
                print a
            for a in  p_a:
                print a
            post_info={
            'url':p_li[1].a['href'][1:],
            'title':smart_str(p_li[1].a['title']),
            'reply':int(p_li[0].text),
            'user_id':int(p_a[-1]['bm_user_id']),
            'user_name':p_a[-1].text,
            'create_time':transtime(p_li[3].text),
            'find_time':time.time(),
            'is_open':1,
            'content':'',
            'is_check':0,
            'click':0,
            }
            print post_info
            post_url=str(os.path.join(root,post_info['url']))
            print 'post_url:',post_url
            post_html=get_html(post_url)
            if post_html is None:
                print ">"*150
                print "下载帖子html失败"
                print ">"*150
                continue
            if 'backHome' in post_html :
                post_info['is_open'] = 0
                post_info['find_time'] =time.time()
            else:
                post_soup = BeautifulSoup(post_html,fromEncoding='gbk')
                post_info['content'] = get_kds_post_reply(post_soup) 
                post_info['find_time'] =post_info['create_time']
            print 'post_info:',post_info
            post_insert(post_info,'kds')

    else:
        print 'get kds mainpage html fail'


def get_kds_post_reply(post_soup):
    """
    获取帖子的回帖
    """
    #post_html = get_html(url)
    #post_soup = BeautifulSoup(post_html,fromEncoding='gbk')
    layer = 0
    reply_data = []
    reply_list =post_soup.find('div',{'id':'detail-content'}) 
    for reply in reply_list:
        if type(reply) == type(reply_list):
            #print '>'*90
            #print '%s楼'%layer
            author = reply.find('div',{'class':'author'})
            p_time = reply.find('div',{'class':'p_time'})
            #print 'user name:',author.a.strong.text
            #print 'user id:',author.a['bm_user_id']
            #print 'create_time:',p_time.text[-19:]
            m = reply.find('div',{'class':'mc'})
            m = m.div
            content = m.contents
            #print 'div:',m
            db_text = ''
            text_template = "%s<br>"
            img_template = """<img src="%s"></img>"""
            for text in content:
                #print 'text:',text
                if text == u'\n':
                    continue
                elif type(text) == type(m):
                    if text.name == 'a' and text.img and text.img.get('onload',None):
                        #print 'img:',text.img['src']
                        db_text += img_template%text.img['src']
                else:
                    #print 'reply:',text
                    db_text += text_template%text
                    
                #print "db_text:",db_text
            reply_info = {'user_name':author.a.strong.text,
                          'user_id':author.a['bm_user_id'],
                          'content':db_text,
                          'create_time':p_time.text[-19:],
            }
            reply_data.append(reply_info)
            #print 'reply_info:',reply_info
            layer +=1
    return reply_data
                
def get_tieba_post(tieba_name='liyi'):
    """
    抓取百度贴白有些的帖子地址
    """
    url = "http://tieba.baidu.com/f?kw=%s"%tieba_name
    tieba_url_root = "http://tieba.baidu.com"
    tieba_html = get_html(url)

    if tieba_html:
        soup = BeautifulSoup(tieba_html,fromEncoding='gbk')
        thread_list = soup.find('ul',{'id':'thread_list'})
        #print 'thread_list:',thread_list
        post_list = thread_list.findAll('li',{'class':'j_thread_list clearfix'})
        #print "post_list:",len(post_list)
        for p in post_list[2:]:
            #print '===================================\n'
            #print 'row:',p
            time.sleep(3)
            div_title = p.find('a',{'class':'j_th_tit'})
            title_text = div_title.text
            org_title = title_text.encode('utf-8')
            filter_title = gfw.replace(org_title)
            if org_title != filter_title:
                print 'title_text:',title_text
                print '>>>>>>>>>>>>>>>>>>>>>>>>>>>发现不和谐帖子!!!!!!!!!!!!!!!!!<<<<<<<<<<<<<<<<<<<<<<<<<<'
                continue
            #print "title:",div_title
            div_author = p.find('div',{'class':'threadlist_author'}).span.a
            #print "author:",div_author
            div_reply = p.find('div',{'class':'threadlist_rep_num'})
            #print "reply:",div_reply
            url = div_title['href'][1:]
            post_url=str(os.path.join(tieba_url_root,url))
            #print "post_url:",post_url
            if div_author is not None:
                #print "author:",div_author.text
                author = div_author.text
            else:
                author = 'diaosi'
            #print "reply:",div_reply.text
            post_info = {
            'url':int(url[2:]),
            'title':title_text,
            'reply':int(div_reply.text),
            'user_name':author,
            'user_id':'',
            'create_time':time.time(),
            'is_open':1,
            'content':None,
            'is_check':0,
            'click':0,
            'find_time':time.time(),
            'tieba_name':tieba_name,
            }
            post_html = get_html(post_url)
            if post_html is None:
                print ">"*150
                print "下载帖子html失败"
                print ">"*150
                continue
            #reply_list = post_soup.findAll('div',{'class':'p_post'})
            #print 'reply_len:',len(reply_list)
            #if len(reply_list) < 1 :
            if 'closeWindow' in post_html :
                post_info['is_open'] = 0
                post_info['find_time'] =int(time.time())
            else:
                is_liang = 0
                post_soup = BeautifulSoup(post_html,fromEncoding='gbk')
                """
                获取帖子总页数
                page_line = post_soup.findAll('li',{'class':'l_pager pager_theme_2'})
                if page_line:
                    last_page = int(page_line[0].findAll('a')[-1]['href'].split('=')[-1])
                    print 'last_page:',last_page
                else:
                    last_page =1
                    print 'just one page this post'
                """
                post_info['content'],is_liang1 = get_tieba_reply(post_soup,sort_name=tieba_name,post_url = post_info['url'])
                is_liang = is_liang | is_liang1
                #print 'post_info:',post_info
                create_time = post_info['content'][0].get('create_time',time.time())
                post_info['create_time'] =post_info['content'][0].get('create_time',0) 
                post_info['find_time'] =post_info['create_time']
                #post_fid=save_post(post_info['url'],post_html,db=tieba)
                #post_info['fid'] = post_fid
                post_html2 = get_html(post_url+'?pn=2')
                #下载第二页
                if post_html2 is not None and 'closeWindow' not in post_html:
                    post_soup = BeautifulSoup(post_html2,fromEncoding='gbk')
                    next_content ,is_liang2= get_tieba_reply(post_soup,sort_name=tieba_name,post_url = post_info['url'],page=2)
                    is_liang = is_liang | is_liang2
                    if next_content:
                        post_info['content'].extend(next_content)
                    post_html3 = get_html(post_url+'?pn=3')
                    #下载第三页
                    if post_html3 is not None and 'closeWindow' not in post_html:
                        post_soup = BeautifulSoup(post_html3,fromEncoding='gbk')
                        next_content ,is_liang3= get_tieba_reply(post_soup,sort_name=tieba_name,post_url = post_info['url'],page=3)
                        is_liang = is_liang | is_liang3
                        if next_content:
                            post_info['content'].extend(next_content)
                        post_html4 = get_html(post_url+'?pn=4')
                        #下载第四页
                        if post_html4 is not None and 'closeWindow' not in post_html:
                            post_soup = BeautifulSoup(post_html4,fromEncoding='gbk')
                            next_content ,is_liang4= get_tieba_reply(post_soup,sort_name=tieba_name,post_url = post_info['url'],page=4)
                            is_liang = is_liang | is_liang4
                            if next_content:
                                post_info['content'].extend(next_content)
                post_info['is_liang']=is_liang
                    
            post_insert(post_info,'tieba')

    else:
        print 'get tieba mainpage html fail'

def get_tieba_post_img(tieba_name='liyi'):
    """
    抓取百度贴白有些的帖子地址
    """
    url = "http://tieba.baidu.com/f?kw=%s"%tieba_name
    tieba_url_root = "http://tieba.baidu.com"
    tieba_html = get_html(url)

    if tieba_html:
        soup = BeautifulSoup(tieba_html,fromEncoding='gbk')
        thread_list = soup.find('ul',{'id':'thread_list'})
        post_list = thread_list.findAll('li',{'class':'j_thread_list'})
        #print "post_list:",len(post_list)
        for p in post_list:
            #print '===================================\n'
            #print 'row:',p
            time.sleep(3)
            div_title = p.find('a',{'class':'j_th_tit'})
            title_text = div_title.text
            org_title = title_text.encode('utf-8')
            filter_title = gfw.replace(org_title)
            if org_title != filter_title:
                print 'title_text:',title_text
                print '>>>>>>>>>>>>>>>>>>>>>>>>>>>发现不和谐帖子!!!!!!!!!!!!!!!!!<<<<<<<<<<<<<<<<<<<<<<<<<<'
                continue
            div_author = p.find('div',{'class':'threadlist_author'}).span.a
            div_reply = p.find('div',{'class':'threadlist_rep_num j_rp_num'})
            url = div_title['href'][1:]
            post_url=str(os.path.join(tieba_url_root,url))
            if div_author is not None:
                author = div_author.text
            else:
                author = 'diaosi'
            post_info = {
            'url':int(url[2:]),
            'title':title_text,
            'reply':int(div_reply.text),
            'user_name':author,
            'user_id':'',
            'create_time':time.time(),
            'is_open':1,
            'content':None,
            'is_check':0,
            'click':0,
            'find_time':time.time(),
            'tieba_name':tieba_name,
            }
            exist_post = tieba.img.find_one({'url':post_info['url']})
            print 'exist_post:',exist_post
            if exist_post:
                print '===================已经下载过次帖子的图片==================='
                continue
            post_html = get_html(post_url)
            if post_html is None:
                print ">"*150
                print "下载帖子html失败"
                print ">"*150
                continue
            #reply_list = post_soup.findAll('div',{'class':'p_post'})
            #print 'reply_len:',len(reply_list)
            #if len(reply_list) < 1 :
            if 'closeWindow' in post_html :
                post_info['is_open'] = 0
                post_info['find_time'] =int(time.time())
            else:
                is_liang = 0
                post_soup = BeautifulSoup(post_html,fromEncoding='gbk')
                """
                获取帖子总页数
                page_line = post_soup.findAll('li',{'class':'l_pager pager_theme_2'})
                if page_line:
                    last_page = int(page_line[0].findAll('a')[-1]['href'].split('=')[-1])
                    print 'last_page:',last_page
                else:
                    last_page =1
                    print 'just one page this post'
                """
                post_info['content'],is_liang1 = get_tieba_reply_img(post_soup,sort_name=tieba_name,post_url = post_info['url'])
                is_liang = is_liang | is_liang1
                post_html2 = get_html(post_url+'?pn=2')
                #下载第二页
                if post_html2 is not None and 'closeWindow' not in post_html:
                    post_soup = BeautifulSoup(post_html2,fromEncoding='gbk')
                    next_content ,is_liang2= get_tieba_reply_img(post_soup,sort_name=tieba_name,post_url = post_info['url'],page=2)
                    post_html3 = get_html(post_url+'?pn=3')
                    #下载第三页
                    if post_html3 is not None and 'closeWindow' not in post_html:
                        post_soup = BeautifulSoup(post_html3,fromEncoding='gbk')
                        next_content ,is_liang3= get_tieba_reply_img(post_soup,sort_name=tieba_name,post_url = post_info['url'],page=3)
    else:
        print 'get tieba mainpage html fail'

def get_tieba_reply(post_soup,sort_name,post_url,page=1):
    """
    解析帖子内容
    """
    print 'post_url:',post_url
    db_name = 'tieba'
    tieba_reply = tieba.reply
    reply_list_tmp = post_soup.findAll('div',{'class':'p_postlist'})
    reply_list = []
    try:
        reply_list.append(reply_list_tmp[0].find('div',{'class':'l_post noborder'}))
        reply_list_tmp = reply_list_tmp[0].findAll('div',{'class':'l_post '})
    except Exception,e:
        print traceback.print_exc()
        print '====================================\n'
        print post_soup
    for r in reply_list_tmp:
        reply_list.append(r)
    #print reply_list[0].text
    #print 'reply_list len:',len(reply_list)
    #time.sleep(999)
    #for r in reply_list:
    #    print '=========================\n'
    #    print r
    #print reply_list[0]
    #print json.loads(reply_list[0]['data-field'])
    #print reply_list[0].findAll('div',{'class':'d_post_content'})
    #return
    rcount = 1
    reply_data = []
    author_name = '' 
    is_liang = 0
    for reply in reply_list:
        #print '>'*150
        #print '第%s楼'%rcount
        #print 'reply:',reply
        #p_author = reply.find('ul',{'class':'p_author'}).findAll('li')
        if reply is None :
            continue
        d_post_content = reply.find('div',{'class':'d_post_content_main '})
        p_tail = reply['data-field']
        if p_tail:
            p_tail = json.loads(p_tail)
            #print 'tpye:',type(p_tail)
            #print 'p_tail:',p_tail
            create_time = transtime(p_tail['content']['date'])
            user_id = p_tail['author'].get('outer_id',-1)
            user_name = p_tail['author']['name']
        else:
            create_time = tim.time()
            user_name = ''
            user_id =-1 

        #print 'd_post_content:',str(d_post_content)
        #print 'user name:',user_name
        #print 'user id:',user_id
        #print 'create_time:',create_time
        reply_content_img_list = d_post_content.findAll('img')
        #print 'reply_content_img_list:',reply_content_img_list
        if rcount ==1 :
            author_name = user_name

        if user_name != author_name:
            #if 'img' in str(d_post_content):
            if reply_content_img_list :
                print '>>>>系统屏蔽了不和谐图！<<<<'
                d_post_content='>>>>系统屏蔽了不和谐图！<<<<'
        else:
            #存储楼主的图片url
            if sort_name == 'meinv':
                for img in reply_content_img_list:
                    #print 'img src:',img['src']
                    reply_img_insert('tieba',sort_name,img['src'],post_url)
            #else:
            #    for img in reply_content_img_list:
            #        reply_img_insert('tieba',sort_name,img['src'],post_url)

        
        content = str(d_post_content)
        org_content = content.encode('utf-8')
        filter_title = gfw.replace(org_content)
        #if org_content != filter_title:
        #    print '>>>>系统屏蔽了不和谐评论！<<<<'
        #    content = '>>>>>>>>>>>系统屏蔽了不和谐评论<<<<<<<<<<'            

        liang_filter = lgfw.replace(org_content)
        if liang_filter != org_content:
            is_liang = 1 

        reply_info = {'user_name':user_name,
                      'user_id':user_id,
                      'content':content,
                      'create_time':create_time,
        }

        #print 'reply_info:',reply_info
        rcount+=1
        reply_data.append(reply_info)
    return reply_data,is_liang


def get_tieba_reply_img(post_soup,sort_name,post_url,page=1):
    """
    解析帖子图片
    """
    print 'post_url:',post_url
    db_name = 'tieba'
    tieba_reply = tieba.reply
    reply_list_tmp = post_soup.findAll('div',{'class':'p_postlist'})
    reply_list = []
    try:
        reply_list.append(reply_list_tmp[0].find('div',{'class':'l_post noborder'}))
        reply_list_tmp = reply_list_tmp[0].findAll('div',{'class':'l_post '})
    except Exception,e:
        print traceback.print_exc()
        print '====================================\n'
        print post_soup
    for r in reply_list_tmp:
        reply_list.append(r)
    rcount = 1
    reply_data = []
    author_name = '' 
    is_liang = 0
    for reply in reply_list:
        if reply is None :
            continue
        d_post_content = reply.find('div',{'class':'d_post_content_main '})
        p_tail = reply['data-field']
        if p_tail:
            p_tail = json.loads(p_tail)
            create_time = transtime(p_tail['content']['date'])
            user_id = p_tail['author'].get('outer_id',-1)
            user_name = p_tail['author']['name']
        else:
            create_time = tim.time()
            user_name = ''
            user_id =-1 

        reply_content_img_list = d_post_content.findAll('img')
        #print 'reply_content_img_list:',reply_content_img_list
        if rcount ==1 :
            author_name = user_name

        if user_name == author_name:
            #存储楼主的图片url
            for img in reply_content_img_list:
                print 'img src:',img['src']
                hostname = urlparse(img['src']).hostname
                if hostname != 'imgsrc.baidu.com':
                    continue
                reply_img_insert('tieba',sort_name,img['src'],post_url)
        rcount +=1

    return reply_data,is_liang
def check_filter_title():
    post_list=tieba.post.find({'is_open':0},limit=50,skip=0,sort=[('find_time',DESCENDING)])
    for p in post_list:
        t = p['title'].encode('utf-8')
        ft = gfw.replace(t)
        print 'url:%s, title:%s,  filter_title:%s   if in :%s'%(p['url'],t,ft,str(ft == t))

def get_tieba_info(tieba_name='liyi'):
    """
    获取贴吧某个吧信息
    """
    db =  connection['tieba']
    post = db.post
    img = db.img
    print '===========================%s info================================='%tieba_name
    print 'total post count:',post.count()
    print 'delete post count:',post.find({'is_open':0,'tieba_name':tieba_name}).count()
    print 'open post count:',post.find({'is_open':1,'tieba_name':tieba_name}).count()
    print 'hexie post count:',post.find({'is_open':-1,'tieba_name':tieba_name}).count()
    print 'img count:',img.find({'type_name':tieba_name}).count()
    print '===================================================================='


if __name__ == "__main__":
    if sys.argv[1] == 'test':
        get_tieba_info()
    elif sys.argv[1] == 'kds':
        while True:
            try:
                get_kds_post()
            except Exception,e:
                print('\n'*9)
                traceback.print_exc()
                print('\n'*9)
    else:
        while True:
            try:
                get_tieba_post("liyi")
                get_tieba_post("liyi")
                get_tieba_post("liyi")
                get_tieba_post("liyi")
                get_tieba_post("liyi")
                get_tieba_post_img("jietup")
            except Exception,e:
                print('\n'*9)
                traceback.print_exc()
                print('\n'*9)

#print get_kds_post_reply('http://club.pchome.net/thread_1_15_7030170.html') #main()
#    print save_post('thread_1_15_6751208__.html','test1',kds)
#    print transtime('11-11-13 12:30')
#    para={'user_id': u'234', 'img': '', 'title': u'\u5ac2\u5b50\u5728\u6211\u5e8a\u4e0a\u8fc7\u4e86\u4e00\u591c......', 'url': u'thread_1_15_6746441__.html', 'is_open:': 1, 'content': '', 'create_time': u'11-12-13 10:30', 'cotent':''}
#    post_insert(para,db=kds)
    #print get_tieba_post("liyi")
    #print get_kds_post()
    #check_filter_title()

    #html = get_html("http://tieba.baidu.com/p/1997596510")
    #post_soup = BeautifulSoup(html,fromEncoding='gbk')
    #print get_tieba_reply(post_soup,'liyi','1997596510')
    
    #print reply_img_insert(db_name = 'tieba',sort_name='liyi',img_url='http://imgsrc.baidu.com/forum/pic/item/0b46f21fbe096b6375fba8f70c338744eaf8acb3.jpg')
    #get_tieba_info()
    #get_tieba_post("jietup")
    #get_tieba_post("liyi")
    #get_tieba_post_img("jietup")
