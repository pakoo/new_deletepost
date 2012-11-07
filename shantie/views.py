# -*- coding: utf-8 -*-
from django.template import loader ,Context
from django.http import HttpResponse , HttpResponseRedirect
from django.shortcuts import render_to_response as render
from mdb import get_delete_post_url,get_tieba_delete_post_url,get_tieba_post_reply
from django.utils.encoding import smart_str, smart_unicode
import os
import pycurl
import traceback
import StringIO
import zlib
import mdb
from django.views.decorators.csrf import csrf_exempt,csrf_protect

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
    return render('mainpage.html',{})


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
    page=int(page)
    frontpage='/tieba/%s/'%(page-1)
    nextpage='/tieba/%s/'%(page+1)
    res = get_tieba_delete_post_url(page=page)
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
        
    return render('hero.html',post_data)


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
    print 'page:',page
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
        
    return render('manage.html',post_data)


def tieba_today_hot(request,page):
    print 'page:',page
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
        
    return render('tieba_backend.html',post_data)


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
    print "post_url:",post_url
    reply_info=get_tieba_post_reply(int(post_url),'tieba')
    hot_post = mdb.get_hot_post('tieba')
    if reply_info:
        return render('tieba.html',{'data':reply_info,'title':reply_info['title'],'floor':1,'hot_post':hot_post})
    else:
        return HttpResponseRedirect('/tieba/1/')
        #return HttpResponse('post have be delete')
        

@csrf_exempt    
def remove_tieba_post(request):
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
