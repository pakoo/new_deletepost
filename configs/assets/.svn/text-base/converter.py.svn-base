#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
从xlsx文件中读取配置并导出到后端配置表

当前仅接受??个xlsx文件，任何対目录的奇怪改动都会导致程序拒绝执行，以最大程度保护数据免遭误操作
'''
from openpyxl import load_workbook

import os
import sys
import re
import time
import logging
from ansistream import ColorizingStreamHandler
logging.StreamHandler = ColorizingStreamHandler
logging.basicConfig(level=logging.DEBUG,format='[%(asctime)s]%(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

PATH = os.path.realpath(__file__)
DIR = os.path.dirname(PATH)

# 检查目录是否仅包含合法信息
configlist = 'events.xlsx,heroes.xlsx,instances.xlsx,levels.xlsx,monsters.xlsx,quest.xlsx,skills.xlsx,talents.xlsx,title_in_church.xlsx,\
city.xlsx,star_position.xlsx,star_cloud.xlsx,quest_receive_condition.xlsx,quest_finish_condition.xlsx,star_awards.xlsx,star_chain.xlsx,monsters.xlsx,\
monster_teams.xlsx,ChurchSKILL.xlsx,item_level.xlsx,item_common.xlsx,hero_level.xlsx,hero_common.xlsx,bar_city.xlsx,bar_search.xlsx,tips.xlsx,awards.xlsx,\
buffs.xlsx,item_shop.xlsx,item_price.xlsx,god.xlsx,church_level.xlsx,church_skill.xlsx,guide_section.xlsx,guide_step.xlsx,first_name.xlsx,last_name.xlsx,awards_online.xlsx,awards_package.xlsx,awards_login.xlsx,vip.xlsx,influence.xlsx,prizeXml.xlsx,dial.xlsx'.split(',')
filelist = []
for name in os.listdir(DIR):
    if name.endswith('xls'):
        if name+'x' in configlist:
            logging.error(u'文件 %s 为97-2003格式的xls文件,请另存为xlsx文件再进行转换' % name)
        else:
            logging.error(u'%s 这文件哪里来的?上传的童鞋请去写检讨' % name )
        sys.exit(1)
    elif name.endswith('xlsx'):
        if name not in configlist:
            logging.error(u'文件 %s 并非已知配置文件，请确认文件名是否上传正确，若不正确，上传者请去写检讨' % name)
            sys.exit(1)
        filelist.append(name)

# 配置表的一些配置:)
assert_json = {'talents.xlsx':['effect','condition'],'item_common.xlsx':['result_of_use'],'skills.xlsx':['effects','buff']}
fname_map = {'ChurchSKILL.xlsx':'church_bonuses.py'}
column_map = {'item_id':'item_iid','item_uid':'item_id','hero_id':'hero_iid','hero_uid':'hero_id',}
index_map = {
    'events.xlsx':['eventID','require_level','prefixEventID'],
    'heroes.xlsx':['hero_iid','level_number','best_position'],
    'instances.xlsx':["fbID","lvLimit","chapter"],
    'levels.xlsx':['bottom_ex','top_ex'],
    'monsters.xlsx':[],
    'monster_teams.xlsx':['monsterId','monsterLv','god_id','room','Gate_id'],
    'quest.xlsx':['quest_id','avatar_level','quest_receive_id','quest_finish_id','category','repeatable'],
    'skills.xlsx':['priority'],
    'talents.xlsx':['category'],
    'title_in_church.xlsx':[],
    'church_level.xlsx':['bottom_ex','top_ex'],
    'church_skill.xlsx':['church_skill_id','church_skill_level'],
    'churchs.xlsx':[],
    'item_level.xlsx':['item_id','item_iid','lv'],
    'item_shop.xlsx':['store_id','level'],
    'item_common.xlsx':['item_quality','item_iid','max_per_stack'],
    'item_price.xlsx':['item_iid','item_id'],
    'star_position.xlsx':['position_id'],
    'star_cloud.xlsx':['cloud_id'],
    'quest_receive_condition.xlsx':[],
    'star_awards.xlsx':['award_id'],
    'star_chain.xlsx':['chain_id'],
    'hero_common.xlsx':['hero_quality'],
    'bar_search.xlsx':['city1','city2','city3'],
    'last_name.xlsx':['gender'],
    'first_name.xlsx':['gender'],
    'awards_online.xlsx':['id'],
    'awards_package.xlsx':['id'],
    'awards_login.xlsx':['id','login_times'],
    'guide_section.xlsx':['sectionID','lvLimit'],
    'vip.xlsx':['id','level','acc_h_money'],
    'influence.xlsx':['id','city_id'],
    'prizeXml.xlsx':['prizeGroupId'],
    'dial.xlsx':['id'],
}


# cell标准化函数
def trans(x):
    """ 把一个cell转换为配置表标准类型 """
    if x == 0:
        return 0
    if not x:
        return ''
    try:
        ret = float(x)
        if abs(ret-int(ret)) <= 0.0001:
            ret = int(ret)
    except:
        try:
            ret = str(x)
        except:
            ret = x
    return ret

# 输出到文件
def output(filepath,config_name,config_list,indexes):
    with open(filepath,'w') as f:
        f.write("#coding:utf-8\n")
        f.write("indexes = %s\n"%indexes)
        f.write("config_name = %s\n"%config_name)
        f.write("config_list = [\n")
        for record in config_list:
            f.write("    %s,\n"%record)
        f.write("]\n")

# 对各个xlsx进行转换
def convert():
    config_path = os.path.join(DIR,"..")
    for fname in filelist:
        #if fname == 'skills.xlsx':
        #    logging.warning('skills are hard to import from xlsx, we will maintain it manually')
        #    continue

        logging.debug('loading configs from %s ...' % fname)
        wb = load_workbook(os.path.join(DIR,fname))
        for sheetname in wb.get_sheet_names():
            sheet = wb.get_sheet_by_name(sheetname)
            break

        config_name = [ str(x.value) if x.value not in column_map else column_map.get(x.value) for x in sheet.rows[1] if x.value ]
        column_length = len(config_name)
        logging.debug('length of column_names: '+str(column_length))

        config_list = []
        for row in sheet.rows[3:]:
            for x in row:
                if x.value:
                    break
            else:
                continue
            if len(row) != column_length:
                logging.warning(u'配置表参数列数与表头列数不匹配,%s != %s,有可能造成潜在的问题' % (len(row),column_length))
            oneline = [ trans(x.value) for x in row[:column_length] ]

            #验证json格式的正确性
            if assert_json.get(fname):
                for col in assert_json[fname]:
                    try:
                        if oneline[config_name.index(col)]:
                            eval(oneline[config_name.index(col)])
                    except:
                        print u"JSON格式不对",oneline[config_name.index(col)]
                        return
            if oneline and oneline[0] is not None:
                config_list.append( oneline )

        indexes = index_map.get(fname,[]) 
        
        nname = fname.replace('xlsx','py') if fname not in fname_map else fname_map.get(fname)
        output_path = os.path.join(config_path,nname)
        #将商店物品转化一下
        import shop_convert
        shop_convert.convert_shop_item()

        logging.info('write to path: '+output_path)
        output(output_path,config_name,config_list,indexes)

if __name__ == "__main__":
    convert()
