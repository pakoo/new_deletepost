#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
from hashlib import md5
#sys.path.insert(0,os.path.join(os.path.dirname(__file__),"../.."))
#from ircd import ircServer, smallgfw

"""汉字处理

判断unicode是否是汉字，数字，英文，或者其他字符。
全角符号转半角符号。
"""

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False

def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar<=u'\u0039':
        return True
    else:
        return False

def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False

def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False

def is_num_str(uchar):
    """判断是否仅有英文和数字"""
    if is_number(uchar) or is_alphabet(uchar):
        return True
    else:
        return False

def B2Q(uchar):
    """半角转全角"""
    inside_code=ord(uchar)
    if inside_code<0x0020 or inside_code>0x7e:     #不是半角字符就返回原来的字符
        return uchar
    if inside_code==0x0020: #除了空格其他的全角半角的公式为:半角=全角-0xfee0
        inside_code=0x3000
    else:
        inside_code+=0xfee0
    return unichr(inside_code)

def Q2B(uchar):
    """全角转半角"""
    inside_code=ord(uchar)
    if inside_code==0x3000:
        inside_code=0x0020
    else:
        inside_code-=0xfee0
    if inside_code<0x0020 or inside_code>0x7e:     #转完之后不是半角字符返回原来的字符
        return uchar
    return unichr(inside_code)

def stringQ2B(ustring):
    """把字符串全角转半角"""
    return "".join([Q2B(uchar) for uchar in ustring])

def uniform(ustring):
    """格式化字符串，完成全角转半角，大写转小写的工作"""
    return stringQ2B(ustring).lower()

def string2List(ustring):
    """将ustring按照中文，字母，数字分开"""
    utmp = []
    retList=[]
    for uchar in ustring:
        if is_other(uchar):
            if len(utmp)==0:
                continue
            else:
                retList.append("".join(utmp))
                utmp=[]
        else:
            utmp.append(uchar)
    if len(utmp)!=0:
        retList.append("".join(utmp))
    return retList

def is_valid_user_name(name):
    """ 验证教会名是否合法 

    只能是数字、英文、中文
    不能是标点符号、空格等
    不能含有敏感词
    只接受unicode
    """
    if isinstance(name, str):
        name = name.decode('utf-8')

    #全角转半角，字母转小写,检测是否存在非法字符
    name = uniform(name)
    valid = True
    for uchar in name:
        if is_other(uchar):
            valid = False
            break

    #检测是否含有敏感词
    #if valid:
    #    # 如果没有gfw，从irc服务器那里初始化全部的东东
    #    if not hasattr(is_valid_church_name, 'gfw'):
    #        is_valid_church_name.gfw = ircServer.gfw
    #        if not is_valid_church_name.gfw:
    #            is_valid_church_name.gfw = smallgfw.GFW()

    #    # 若过滤结果与原来不同，则也不合法
    #    name = name.encode('utf-8')
    #    newname = is_valid_church_name.gfw.replace(name)
    #    print name, newname
    #    if newname != name:
    #        valid = False
    return valid 

def md5_str(encode_str):
    """
    md5一个字符
    """
    m = md5()
    m.update(encode_str)
    return m.hexdigest()

if __name__=="__main__":
    #for i in range(0x0020,0x007F):
    #    print Q2B(B2Q(unichr(i))),B2Q(unichr(i))
 
    #test uniform
    #ustring=u'中国 人名ａ高频Ａ'
    #ustring=uniform(ustring)
    #ret=string2List(ustring)
    #print ret
    #a = '你妈'.decode()
    #print 'len:',len(a)
    #print is_valid_church_name(a)
    print is_num_str('as1234df'.decode('utf-8'))
    #print md5_str('asdfsadaf')
