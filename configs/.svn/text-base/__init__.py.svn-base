#coding:utf-8
import os
import sys
import imp
import random
from operator import itemgetter
imp.load_source("SortedCollection",os.path.join(os.path.dirname(os.path.abspath(__file__)),"../utils/SortedCollection.py"))

class BaseDict:
    def __init__(self,indexes=[]):
        self.indexes = {}
        for idx in indexes:
            self.indexes[idx] = sys.modules['SortedCollection'].SortedCollection(key=itemgetter(0))

    def get(self,**kwargs):
        try:
            pk = kwargs.get('pk')
            if pk:
                return self.__dict__.get('_%s'%pk)
            else:
                return random.choice(self.find(**kwargs))
        except Exception:
            return None

    def find(self,**kwargs):
        '''similar to common sense find

        support "__" operatations, e.g. ge,gt,le,lt,...
        >>> xx.find(exp__ge=1234)
        >>> xx.find(exp__le=1234,limit=1)
        >>> xx.find(exp=1234)
        >>> xx.find(exp__ge=1,level__le=14)
        '''
        pks = set([])
        limit = kwargs.get('limit',None)
        if limit:
            kwargs.pop('limit')

        if not kwargs:
            pks = (pk for pk in self.__dict__.keys() if pk.startswith("_"))
            ret = []
            for pk in pks:
                ret.append( self.__dict__.get(pk) )
            return ret

        pks = None
        for k,v in kwargs.items():
            tmppks = set([])
            if k == 'pk':
                tmppks.add(v)
            else:
                if "__" in k:
                    key,op = k.split("__")
                    if key in self.indexes:
                        for value,key in getattr(self.indexes[key],'find_'+op)(v,limit):
                            tmppks.add(key)
                elif self.indexes.has_key(k):
                    try:
                        eqs = self.indexes[k].find_eq(v)
                    except ValueError:
                        eqs = []
                    for value,key in eqs:
                        tmppks.add(key)
            if pks is None:
                pks = tmppks
            else:
                pks = pks.intersection(tmppks)
        ret = []
        for pk in pks:
            item = self.__dict__.get(pk)
            if item:
                ret.append(item)
        return ret

    def set_name_value(self,name,value,key,d):
        self.__dict__[name] = value
        if name in d.get('indexes'):
            try:
                d.get('indexes')[name].insert( (value,key) )
            except:
                pass

    def __str__(self):
        return "<BaseDict>: %s"%str(self.__dict__.items())

    def __repr__(self):
        return "<BaseDict>: %s"%str(self.__dict__.items())

def load(cname,config_name,config_list,indexes):
    #cname = __file__.split('.')[0].lower()
    globals()[cname] = BaseDict(indexes=indexes)
    dd = globals()[cname]
    d = dd.__dict__
    for config in config_list:
        key = "_%s"%config[0]
        d[key] = BaseDict()
        for i in range(len(config)):
            d[key].set_name_value(config_name[i],config[i],key,d)

'''
Should be used like this

>>> from config import *
>>> h = heroes.get(id=1)
>>> h.name,h.hp
'''
for name in os.listdir(os.path.dirname(os.path.abspath(__file__))):
    if name.endswith(".py") and name not in ["__init__.py","common.py","signal_list.py","talents_mod.py","to_db.py","consts.py","shop_item.py","secretkey.py"]:
        cname = name.rsplit(".",1)[0]
        imp.load_source(cname,os.path.join(os.path.dirname(os.path.abspath(__file__)),name))
        load(cname, getattr(sys.modules[cname],'config_name'),
            getattr(sys.modules[cname],'config_list'),getattr(sys.modules[cname],'indexes'))
