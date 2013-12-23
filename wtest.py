#/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
appid= "wx17fb59e746769663"
appsecret = "53ee138a155220d7614b25a28dcccd18"

def get_access_token(appid,appsecret):
    """
    获取app access token
    """
    token_url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s"%(appid,appsecret)
    access_token = json.loads(requests.get(token_url).text)['access_token']
    return access_token
    

menu = {"button":[
    {
        "name":"关于我们",
        "sub_button":[
            {
                "type":"click",
                "name":"简介",
                "key":"about",
            },

            {
                "type":"view",
                "name":"公司首页",
                "url":"http://www.hanfook.com.cn/",
            },
            ]
    },

    {
        "type":"click",
        "name":"产品列表",
        "key":"products",
    },

    {
        "name":"其他",
        "sub_button":[
            {
                "type":"view",
                "name":"新闻动态",
                "url":"http://www.hanfook.com.cn/news/?class_id=1",
            },

            {
                "type":"view",
                "name":"在线留言",
                "url":"http://www.hanfook.com.cn/feedback/",
            },

            {
                "type":"view",
                "name":"技术支持",
                "url":"http://www.hanfook.com.cn/news/?class_id=2",
            },

            {
                "type":"view",
                "name":"招贤纳士",
                "url":"http://www.hanfook.com.cn/html_info/job-5.html",
            },
            ]
    },
]
}


data = """
-d '{"button": [{"name": "关于我们", "sub_button": [{"type": "click", "name": "简介", "key": "about"}, {"url": "http://www.hanfook.com.cn/", "type": "view", "name": "公司首页"}]}, {"type": "click", "name": "产品列表", "key": "products"}, {"name": "其他", "sub_button": [{"url": "http://www.hanfook.com.cn/news/?class_id=1", "type": "view", "name": "新闻动态"}, {"url": "http://www.hanfook.com.cn/feedback/", "type": "view", "name": "在线留言"}, {"url": "http://www.hanfook.com.cn/news/?class_id=2", "type": "view", "name": "技术支持"}, {"url": "http://www.hanfook.com.cn/html_info/job-5.html", "type": "view", "name": "招贤纳士"}, {"key":"findme", "type": "click", "name": "联系方式"}]}]}'
"""
url = 'curl https://api.weixin.qq.com/cgi-bin/menu/create\?access_token\=%s '%get_access_token(appid,appsecret)

def create_menu(menu,access_token):
    """
    创建菜单
    """
    url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s"%access_token
    r = requests.post(url,data=menu)
    print r.text

def get_menu():
    access_token = get_access_token(appid,appsecret)
    r= requests.get("https://api.weixin.qq.com/cgi-bin/menu/get?access_token=%s"%access_token)
    print r.text

if __name__ == '__main__':
    #access_token = get_access_token(appid,appsecret)
    #print create_menu(menu,access_token)
    #print len(menu['button'])
    #print json.dumps(menu)
    print url
    print data
    #print get_menu()
