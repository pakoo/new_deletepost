 #-*- coding: utf-8 -*-
from django.template import loader ,Context
from django.http import HttpResponse , HttpResponseRedirect
from django.shortcuts import render_to_response as render,render_to_response
from mdb import get_delete_post_url,get_tieba_delete_post_url,get_tieba_post_reply
from django.utils.encoding import smart_str, smart_unicode
import os
import pycurl
import traceback
import StringIO
import zlib
import mdb
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.core.signals import request_finished
from django.dispatch import receiver
import random
import time

#pv=0
#@receiver(request_finished)
#def add_page_view(sender, **kwargs):
#    global pv
#    pv+=1
#    print 'sender:',sender,dir(sender)
#    r = sender.request_class
#    #print 'sender url:',r.get_full_path()
#    print 'argv:',dir(kwargs['signal']),
#    print ">>>>>>>>>>>>>>>>>>>>>>>又完成了一个请求!!!" 
#    print "page view=%s"%pv
def is_login(func) :
    """
    判断用户是否登录
    """
    def check(request,*args,**kargs):
        user_session =request.session 
        print 'user_session is_login:',user_session.get('is_login',0)
        #if user_session.get('sessionid',0):
        if user_session.get('is_login',0) != 1: 
            return HttpResponseRedirect('/admin')
        else:
            return func(request,*args,**kargs) 
    return check

def deflate(data):
    try:
        return zlib.decompress(data,-zlib.MAX_WBITS)
    except zlib.error:
        return zlib.decompress(data)

def get_html(url):
    html=''
    print 'curl:',url
    try:
        crl = pycurl.Curl()
        crl.setopt(pycurl.VERBOSE,1)
        crl.setopt(pycurl.FOLLOWLOCATION, 1)
        crl.setopt(pycurl.MAXREDIRS, 5)
        crl.fp = StringIO.StringIO()
        crl.setopt(pycurl.URL,url)
        crl.setopt(crl.WRITEFUNCTION, crl.fp.write)
        crl.perform()
        html=crl.fp.getvalue()
        crl.close()
    except Exception,e:
        print('\n'*9)
        traceback.print_exc()
        print('\n'*9)
        crl.close()
        return None
    return html

def mainpage(request):
    #print 'session id:',request.session['sessionid']
    print 'cookie:',request.COOKIES
    #res =  request.session.test_cookie_worked()
    #if res:
    #    print 'test cookie:',res
    #else:
    #    request.session.set_test_cookie()
    #uid = request.session.get('uid',None)
    #if uid:
    #    print 'session uid:',uid
    #else:
    #    request.session['uid'] = random.random()
    #response  = render_to_response('mainpage.html', {}) 
    #response.set_cookie("my_cookie",'cookie value')
    #return response
    return HttpResponseRedirect('/real/1/')


def xkds_mainpage(request):
    return HttpResponseRedirect('/kds/1/')
    
def xkds(request,page):
    print 'page:',page
    page=int(page)
    frontpage='/kds/%s/'%(page-1)
    nextpage='/kds/%s/'%(page+1)
    res = get_delete_post_url(page=page)
    #print 'data:',data
    if not res:
        return HttpResponse('no delete post')
    else:
        data,post_amount=res
    post_data={'posts':data}
    post_data['total_amount']=post_amount
    if page >1:
        post_data['frontpage']=frontpage
    else:
        post_data['frontpage']=None
    post_data['nextpage']=nextpage
        
    return render('kds.html',post_data)

def diba(request,page):
    print 'page:',page
    agent = request.META.get('HTTP_USER_AGENT','')
    page=int(page)
    frontpage='/tieba/%s/'%(page-1)
    nextpage='/tieba/%s/'%(page+1)
    res = get_tieba_delete_post_url(page=page)
    #print 'data:',data
    if not res:
        return render('hero.html',{})
    else:
        data,hot_post,total_amount=res
    post_data={'posts':data,
               'total_amount':total_amount,
               'hot_post':hot_post,
                }
    if page >1:
        post_data['frontpage']=frontpage
    else:
        post_data['frontpage']=None
    post_data['nextpage']=nextpage
    post_data['liyi']='active'
    #print 'HTTP_USER_AGENT:',request.META.get('HTTP_USER_AGENT',{})
    #if 'IE' in agent:
    #    print "发现傻逼IE!!!!!!!!!!!!!"
    #    return render('diba.html',post_data)
    return render('hero.html',post_data)

def real(request,page):
    """
    返回玩家正在看得帖子
    """
    print 'page:',page
    agent = request.META.get('HTTP_USER_AGENT','')
    page=int(page)
    frontpage='/real/%s/'%(page-1)
    nextpage='/real/%s/'%(page+1)
    res = mdb.get_tieba_today_hot_post_url(page=page)
    #print 'data:',data
    if not res:
        return render('hero.html',{})
    else:
        data,hot_post,total_amount=res
    post_data={'posts':data,
               'total_amount':total_amount,
               'hot_post':hot_post,
                }
    if page >1:
        post_data['frontpage']=frontpage
    else:
        post_data['frontpage']=None
    post_data['nextpage']=nextpage
    post_data['real']='active'
    return render('hero.html',post_data)


def filter_post_list(request,page):
    """
    返回被和谐的帖子列表
    """
    user_session =request.session 
    print 'user_session is_login:',user_session.get('is_login',0)
    #if user_session.get('sessionid',0):
    if user_session.get('is_login',0) != 1: 
        return HttpResponseRedirect('/admin')
    print 'page:',page
    agent = request.META.get('HTTP_USER_AGENT','')
    page=int(page)
    frontpage='/filter/%s/'%(page-1)
    nextpage='/filter/%s/'%(page+1)
    res = mdb.get_filter_post_url(page=page)
    #print 'data:',data
    if not res:
        return HttpResponse('no delete post')
    else:
        data,hot_post,total_amount=res
    post_data={'posts':data,
               'total_amount':total_amount,
               'hot_post':hot_post,
                }
    if page >1:
        post_data['frontpage']=frontpage
    else:
        post_data['frontpage']=None
    post_data['nextpage']=nextpage
    post_data['filter']='active'
    return render('manage.html',post_data)


def kds_backend(request,page):
    print 'page:',page
    page=int(page)
    frontpage='/kds/manage/%s/'%(page-1)
    nextpage='/kds/manage/%s/'%(page+1)
    res = get_delete_post_url(page,50)
    #print 'data:',data
    if not res:
        return HttpResponse('no delete post')
    else:
        data,post_amount=res
    post_data={'posts':data}
    post_data['total_amount']=post_amount
    if page >1:
        post_data['frontpage']=frontpage
    else:
        post_data['frontpage']=None
    post_data['nextpage']=nextpage
        
    return render('kds_backend.html',post_data)
    
def tieba_backend(request,page):
    #print 'session id:',request.session['sessionid']
    print 'page:',page
    user_session =request.session 
    print 'user_session is_login:',user_session.get('is_login',0)
    #if user_session.get('sessionid',0):
    if user_session.get('is_login',0) != 1: 
        return HttpResponseRedirect('/admin')
    page=int(page)
    frontpage='/tieba/manage/%s/'%(page-1)
    nextpage='/tieba/manage/%s/'%(page+1)
    res = get_tieba_delete_post_url(page=page)
    #print 'data:',data
    if not res:
        return HttpResponse('no delete post')
    else:
        data,hot_post,post_amount=res
    post_data={'posts':data}
    post_data['total_amount']=post_amount
    if page >1:
        post_data['frontpage']=frontpage
    else:
        post_data['frontpage']=None
    post_data['nextpage']=nextpage
    post_data['admin']='active'
        
    return render('manage.html',post_data)


def tieba_today_hot(request,page):
    #print 'session id:',request.session['sessionid']
    print 'page:',page
    user_session =request.session 
    print 'user_session is_login:',user_session.get('is_login',0)
    #if user_session.get('sessionid',0):
    if user_session.get('is_login',0) != 1: 
        return HttpResponseRedirect('/admin')
    page=int(page)
    frontpage='/tieba/hot/%s/'%(page-1)
    nextpage='/tieba/hot/%s/'%(page+1)
    res = mdb.get_tieba_today_hot_post_url(page=page)
    #print 'data:',data
    if not res:
        return HttpResponse('no delete post')
    else:
        data,hot_post,post_amount=res
    post_data={'posts':data}
    post_data['total_amount']=post_amount
    if page >1:
        post_data['frontpage']=frontpage
    else:
        post_data['frontpage']=None
    post_data['nextpage']=nextpage
    post_data['hot']='active'
        
    return render('manage.html',post_data)

#def tieba_today_hot(request,page):
#    print 'page:',page
#    page=int(page)
#    frontpage='/tieba/hot/%s/'%(page-1)
#    nextpage='/tieba/hot/%s/'%(page+1)
#    res = mdb.get_tieba_today_hot_post_url(page=page)
#    #print 'data:',data
#    if not res:
#        return HttpResponse('no delete post')
#    else:
#        data,hot_post,post_amount=res
#    post_data={'posts':data}
#    post_data['total_amount']=post_amount
#    if page >1:
#        post_data['frontpage']=frontpage
#    else:
#        post_data['frontpage']=None
#    post_data['nextpage']=nextpage
#        
#    return render('tieba_backend.html',post_data)


def search_post(request,keyword,page):
    print 'keyword:',keyword
    print 'page:',page
    page=int(page)
    frontpage='/search/%s/%s/'%(keyword,(page-1))
    nextpage='/search/%s/%s/'%(keyword,(page+1))
    res = mdb.search_post(keyword,page)
    if not res:
        return HttpResponse('no delete post')
    else:
        data,hot_post,post_amount=res
    post_data={'posts':data}
    post_data['total_amount']=post_amount
    if page >1:
        post_data['frontpage']=frontpage
    else:
        post_data['frontpage']=None
    post_data['nextpage']=nextpage
        
    return render('tieba_backend.html',post_data)

def get_kds_post(request,post_url):
    print "post_url:",post_url
    reply_info=get_tieba_post_reply(post_url+'.html','kds')
    if reply_info:
        return render('kds_post.html',{'data':reply_info,'title':reply_info['title'],'floor':1})
    else:
        return HttpResponseRedirect('/kds/1/')
        #return HttpResponse('post have be delete')

def get_tieba_post(request,post_url):
    """
    返回帖子内容
    """
    user_session =request.session 
    print user_session.keys()
    print 'user_session is_login:',user_session.get('is_login',0)
    print 'user_sessionid:',user_session.session_key
    print "post_url:",post_url
    reply_info=get_tieba_post_reply(int(post_url),'tieba',mdb.debug_flag)
    hot_post = mdb.get_hot_post('tieba')
    if reply_info:
        return render('tieba.html',{'data':reply_info,'title':reply_info['title'],'floor':1,'hot_post':hot_post})
    else:
        return HttpResponseRedirect('/real/1/')
        #return HttpResponse('post have be delete')
        

def get_filter_post(request,post_url):
    """
    返回被和谐的帖子
    """
    print "post_url:",post_url
    reply_info=get_tieba_post_reply(int(post_url),'tieba',-9)
    hot_post = mdb.get_hot_post('tieba')
    if reply_info:
        return render('tieba.html',{'data':reply_info,'title':reply_info['title'],'floor':1,'hot_post':hot_post})
    else:
        return HttpResponseRedirect('/real/1/')
        #return HttpResponse('post have be delete')

@csrf_exempt    
def remove_tieba_post(request):
    """
    删除帖子
    """
    user_session =request.session 
    print 'user_session is_login:',user_session.get('is_login',0)
    if user_session.get('is_login',0) != 1: 
        return HttpResponse('不要做坏事哦!')
    post_url = request.POST['url']
    print 'post_url:',post_url
    if post_url:
        post_url=post_url.split('/')[-1]
        print 'post_url:',post_url
        res=mdb.delete_post(post_url,'tieba')
        print 'res:',res
    return HttpResponse(res)

@csrf_exempt    
def remove_kds_post(request):
    user_session =request.session 
    print 'user_session is_login:',user_session.get('is_login',0)
    if user_session.get('is_login',0) != 1: 
        return HttpResponse('不要做坏事哦!')
    post_url = request.POST['url']
    print 'post_url1:',post_url
    if post_url:
        post_url=post_url.split('/')[-1]
        print 'post_url:',post_url
        res=mdb.delete_post(post_url,'kds')
        print 'res:',res
    return HttpResponse(res)

@csrf_exempt    
def get_kds_post_total_amount(request):
    """
    获取现在帖子的总数
    """
    return HttpResponse(mdb.kds.post.count())
    
@csrf_exempt    
def get_tieba_post_total_amount(request):
    """
    获取现在帖子的总数
    """
    return HttpResponse(mdb.tieba.post.count())
    
    
def zhongzi(request):
    fuli_path="/srv/media/media/zhongzi"
    #fuli_path="D:/download/fs2yougd"
    root_url="/media/zhongzi/"
    html_temp="""<!DOCTYPE html><html>
                        <head>
                        <meta charset="utf-8"/>
                        <title>crazy people</title>
                        </head>
                        <body>
                        %s
                        </body>
                        <html>"""
    url_temp="""<p><a href="%s">%s</a></p>"""
    fuli_html=''
    fuli_file_list=os.listdir(fuli_path)
    print 'fuli_file_list:',fuli_file_list
    for file in fuli_file_list:
        url=os.path.join(root_url,file)
        file_name=file
        fuli_html+=url_temp%(url,file_name)
    print html_temp%fuli_html
    return HttpResponse(html_temp%fuli_html)

def save_html(request,url):
    print 'url:',url,type(url)
    html = get_html(str(url))
    print type(html)
    return HttpResponse(html)

def advice_board(request):
    """
    留言版
    """
    return render('advice.html',{'advice':'active'})


def manage_login(request):
    """
    后台登录页
    """
    user_session =request.session 
    print 'user_session is_login:',user_session.get('is_login',0)
    if user_session.get('is_login',0) == 1:
            return HttpResponseRedirect('/tieba/manage/1/')
    return render('admin.html',{})

@csrf_exempt    
def admin_login(request):
    """
    管理员登录
    """
    print 'POST:',request.POST
    user_session =request.session 
    print 'user_session is_login:',user_session.get('is_login',0)
    user_name = request.POST.get('username','')
    password = request.POST.get('password','')
    if len(user_name) > 10 or len(password) >20:
        return HttpResponse('用户名密码错误')
    else:
        if mdb.user_login(user_name,password) == 1:
            user_session['is_login'] = 1
            return HttpResponseRedirect('/tieba/manage/1/')
        else:
            return HttpResponse('用户名密码错误')
            
def admin_logout(request):
    """
    管理员登出
    """
    user_session =request.session 
    print 'user_session is_login:',user_session.get('is_login',0)
    user_session['is_login'] = 0
    return HttpResponse('退出成功!')


@csrf_exempt    
def send_advice(request):
    """
    发送建议
    """
    ip = request.META['REMOTE_ADDR']
    print 'ip:',ip
    print 'POST:',request.POST
    nick_name = request.POST.get('nickname','') 
    content = request.POST.get('advice','') 
    if len(nick_name) > 20 or len(content) >140:
        return HttpResponse('留言字数过多,最多140字!')
    else:
        mdb.add_advice(content,nick_name,ip)
    return HttpResponse('给站长留言成功!')
@is_login
def advice_message(request):
    """
    留言板信息
    """
    message = mdb.get_advice()
    return render('advice_board.html',{'mlist':message})

@csrf_exempt    
@is_login
def hide_post(request):
    """
    隐藏帖子
    """
    post_url = request.POST['url']
    print 'post_url:',post_url
    if post_url:
        post_id=post_url.split('/')[-1]
        print 'post_id:',post_id
        res=mdb.hide_post(post_id,'tieba')
        print 'res:',res
    return HttpResponse(res)
        
def tu(request,page=1):
    """
    图片列表
    """
    #pic_url = '71cf3bc79f3df8dc7fa3ae06cd11728b4610288e.jpg.jpg'
    #return render('tu.html',{'src':'http://imgsrc.baidu.com/forum/pic/item/'+pic_url})
    page = int(page)
    img_list = []
    img_list = mdb.get_tu(page,'jietup',24)
    #img_list = [{'post_url':a['post_url'],'url':a['url']} for a in img_list]
    print img_list
    return render('tu.html',{'img_list':img_list,'tu':'active','frontpage':page-1,'nextpage':page+1})

@csrf_exempt    
def write_reply(request):
    """
    发表评论
    """
    url = request.META['HTTP_REFERER'].split('/')[-1]
    user_session =request.session 
    print 'user_session is_login:',user_session.get('is_login',0)
    print 'user_sessionid:',user_session.get('sessionid',0)
    print 'url :',url
    if user_session.get('last_reply_time',None):
        last_reply_time = int(user_session.get('last_reply_time'))
        print 'last_reply_time:',last_reply_time
        if time.time()-last_reply_time <= 30:
            return  HttpResponse('评论间隔太多请等30秒后再提交评论!!')
    text = request.POST.get('text','')
    print 'text:',text
    if text:
        if len(text) >300:
            return  HttpResponse('字数太多超过300字了!!')

        else:
            reply_info = {
                'content':text,
                'user_id':-1,
                'create_time':int(time.time()),
                'user_name':'404网友',
                'session_key':getattr(user_session,'session_key',''),
            } 
            mdb.add_new_reply(int(url),reply_info)
            user_session['last_reply_time'] = int(time.time())
        return  HttpResponseRedirect('/tieba/post/%s'%url)
    else:
        return  HttpResponse('添加失败')
        
@csrf_exempt    
@is_login
def remove_tu(request):
    """
    删除图片
    """
    print '================>>>>>>>>>>>>remove_tu'
    post_url = request.POST['url']
    print 'post_url:',post_url
    if post_url:
        res=mdb.delete_tu(post_url)
        print 'res:',res
    return HttpResponse(res)

def tu_manage(request,page=1):
    """
    图片列表
    """
    page = int(page)
    img_list = []
    img_list = mdb.get_tu(page,'jietup',30)
    print img_list
    return render('tu_manage.html',{'img_list':img_list,'manage_tu':'active','frontpage':page-1,'nextpage':page+1})

@csrf_exempt    
@is_login
def hide_tu(request):
    """
    删除图片
    """
    post_url = request.POST['url']
    print 'post_url:',post_url
    if post_url:
        res=mdb.hide_tu(post_url)
        print 'res:',res
    return HttpResponse(res)

def register(request):
    """
    注册页面
    """

    request.session['return_url']=request.META['HTTP_REFERER']
    return render('register.html',{})


@csrf_exempt    
def create_new_user(request):
    """
    注册
    """
    ip = request.META['REMOTE_ADDR']
    username = request.POST.get('username','').strip()
    password = request.POST.get('password','').strip()
    return_url = request.session['return_url']
    print 'return_url  url:',request.session['return_url']
    if username and password:
        uid = mdb.create_user(username,password,ip)
        print 'uid:',uid
        return_path = return_url.split('/',3)[-1]
        if uid:
            #print 'return  path:',return_path
            if return_path.replace('/','') == 'register':
                return_url = '/'
            else:
                return_url = '/'+return_path
            request.session['is_login']=1
            request.session['name']=username
            request.session['uid']=uid
            #print 'return url:',return_url
            response  = render_to_response('info.html', {'content':"注册成功!",'title':'注册成功','return_url':return_url}) 
            response.set_cookie("username",username)
            return response
        else:
            pass
    else:
        pass
    return HttpResponse('fail')

def login_page(request):
    """
    登录页面 
    """
    refer_url = request.META['HTTP_REFERER']
    return_path = refer_url.split('/',3)[-1]
    if return_path.replace('/','') == 'userlogin':
        return_url = '/'
    else:
        return_url = '/'+return_path
    request.session['return_url']=return_url
    print 'return_url:',return_url
    return render('login.html',{})

def user_logout(request):
    """
    用户登出
    """
    request.session['is_login']=0
    #response  = render_to_response('info.html', {'content':"退出登录成功!",'title':'登出','return_url':'/'}) 
    response = real(request,1)
    response.set_cookie("username",'')
    return response

@csrf_exempt    
def user_login(request):
    """
    用户登录
    """
    username = request.POST.get('username','').strip()
    password = request.POST.get('password','').strip()
    uid = mdb.check_login(username,password)
    if uid:
        request.session['is_login']=1
        request.session['name']=username
        request.session['uid']=uid
        response  = render_to_response('info.html', {'content':"登录成功!",'title':'登录成功','return_url':request.session['return_url']}) 
        response.set_cookie("username",username)
        return response
    else:
        response  = render_to_response('info.html', {'content':"密码错误!",'title':'失败','return_url':'/userlogin'}) 
        return response
        
        

def info(request):
    """
    提示页面
    """
    return render('info.html',{'content':"这是一个神奇的敌方!"})



