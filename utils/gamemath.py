#coding:utf-8
import re
import math
import random
import bisect
from configs.common import hero_properties

#def GFS(lvl):
#    Rlvl=[0]*80
#    for i in range(1,81):
#        Rlvl[i-1]=(i<=60)*1.+(i>60)*(0.5**((i-60.)*0.1))
#    return sum(Rlvl[:lvl])

def random_choose(datalist,probname='probability'):
    selected = None

    probs = [ getattr(dl,probname) for dl in datalist ]            
    for i in range(1,len(probs)):
        probs[i] += probs[i-1]
    
    probs = probs
            
    try:
        rand = random.random()
        index = bisect.bisect_left(probs,rand)
        selected = datalist[index]
    except IndexError:
        # we don't have a match in this priority level
        # go on to next level
        pass
    return selected

def exp_to_prestige(exp):
    return 10*(1-math.log(-exp/1000000))

def calculate_fighting_points(v1, v0, lv, add1, add2, ratio, cskills=[]):
    '''根据英雄的属性值计算属性数
    
    values: 二维矩阵，分别代表八个属性的 (v1,v0,lv,add1,add2,add3)
    其中:
        
        # v1 初始值
        # v0 分配比例
        # lv 等级
        # add1 直接增加的点数值
        # add2 按百分比附加的点数值(天赋等)，现已排除次加成可能，故add2=[0]*8
        # ratio 在某位置上的实力发挥效率，已排除此功能，故ratio恒为1
        # cskills 教会技能加成，同样包含两种情况：
        #  1、纯数值加成；2、百分比加成（已经排除）
    '''
    C = 1/10000.
    X = 1000
    lg = math.log(ratio)
    y = 1+lg/C/X
    # 计算等级为lv的裸装英雄数值
    funcs = [
        lambda v1,v0: v1*math.exp(C*v0*y*X*lv),
        lambda v1,v0: 1-(1-v1)*math.exp(-C*v0*y*X*lv),
        lambda v1,v0: 1-(1-v1)*math.exp(-C*v0*y*X*lv),
        lambda v1,v0: v1*math.exp(C*v0*y*X*lv),
        lambda v1,v0: v1*math.exp(C*v0*y*X*lv),
        lambda v1,v0: v1*math.exp(C*v0*y*X*lv),
        lambda v1,v0: (1+v1)*math.exp(C*v0*y*X*lv)-1,
        lambda v1,v0: 1-(1-v1)*math.exp(-C*v0*y*X*lv),
    ]
    # 计算加成后的战斗用数值
    fightfuncs = [
        lambda x,add1,add2: (x+add1)*(1+add2),
        lambda x,add1,add2: 1-(1-x)*(1-add1/(1000.+add1)),
        lambda x,add1,add2: 1-(1-x)*(1-add1/(1000.+add1)),
        lambda x,add1,add2: (x+add1)*(1+add2),
        lambda x,add1,add2: (x+add1/100.)*(1+add2),
        lambda x,add1,add2: x+add1/1000.,
        lambda x,add1,add2: x+add1/1000.,
        lambda x,add1,add2: 1-(1-x)*(1-add1/(1000.+add1)),
    ]
    # 计算显示用数值（此部分功能曾被用来计算加成后的效果，先用来加成裸装显示效果）
    dispfuncs = [
        lambda x: int(math.ceil(x)),
        lambda x: int(math.ceil(1000.*x/(1-x))),
        lambda x: int(math.ceil(1000.*x/(1-x))),
        lambda x: int(math.ceil(x)),
        lambda x: int(math.ceil(x*100.)),
        lambda x: int(math.ceil(1000.*x)),
        lambda x: int(math.ceil(1000.*x)),
        lambda x: int(math.ceil(1000.*x/(1-x))),
    ]
    # 如果有教会技能加成，加成效果将分别附加在add1和add2中
    if cskills:
        add1 = map(sum,zip(cskills['add1'],add1))
        add2 = map(sum,zip(cskills['add2'],add2))
    # 等级为lv的裸装数值
    rawpoints   = [ funcs[i](v1[i],v0[i]) for i in range(8) ]
    # 战斗用数值
    fightpoints = [ fightfuncs[i](rawpoints[i], add1[i], add2[i]) for i in range(8) ]
    # 显示用数值
    disppoints  = map(sum,zip([ dispfuncs[i](rawpoints[i]) for i in range(8) ],add1))
    # 返回结果
    return fightpoints, disppoints

def fighting_points_to_power(values):
    '''根据英雄的属性数生成战斗力
    values: 生命,防御,格档,攻击,速度,命中,暴击,连击
    '''
    h,d,t,a,s,r,b,g = values
    return int(round(math.sqrt(h*a*s*r*(1+b)/(1-d)/(1-t)/(1-g))))
    #p = h*a*s*r*(1+b)/(1-d)/(1-t)/(1-g)
    #return int(math.pow(max(math.log(p/20000.),0),2.7)/math.log(1.02))
    #return int(100*math.log(p/19000.))


def calc_fuben_fight(fuben_level):
    """
    计算副本的经验
    """
    c_r = 1.12910261102257
    c_a = 8.47297860387204
    c_c = 1/4750.0
    c_x = 1000.0
    c_cx = c_x*c_c
    exp =int(round(100*(math.exp(c_cx)-1)*math.exp(fuben_level*c_cx)/c_r**(fuben_level-1)/2.0/1.2))
    return exp



def BasicAward(level):
    """
    计算基本战斗奖励（经验+银币）
    1、输入参数：level（玩家等级，从1到100）；
    2、输出结果:Exp（经验奖励），Silver（银币奖励）
    """
    # 基本参数
    DaySpirit=200+40*2+40 #一天最大体力数（每天按照四个小时计算，包含一天总体力200，12:00和20:00各送的40，以及保守自然恢复的40）
    SpiritCost_SingleComplex=5 #% 单个副本体力消耗
    ComplexAverageFights=3+2 #单个副本战斗场数（战斗3场，通关奖励相当于2场战斗奖励的数额）
    SpiritCost_SingleWarmup=3 #单场热身赛体力消耗
    ComplexPercentage=0.5 #一天全部体力分配到副本中的百分比
    WarmupPercentage=0.5 #一天全部体力分配到热身赛中的百分比
    # 衍生参数
    ComplexFightsPerDay=DaySpirit*ComplexPercentage/SpiritCost_SingleComplex*ComplexAverageFights #一天的全部体力用来刷副本，可以进行的战斗场数
    WarmupFightsPerDay=DaySpirit*WarmupPercentage/SpiritCost_SingleWarmup #一天的全部体力用来打热身赛，可以进行的战斗场数
    # 计算过程
    if level<=100:
        # 该级需要的天数
        DayCostThisLevel=1.902*math.exp(0.03852*level)*(math.exp(0.03852)-1)
        # 经验
        C,X,lamda=0.0001,1000,0.001 #固有参数
        SubExp=math.exp(C*X*(level+1))*(1-math.exp(-C*X))/lamda #本等级段经验总量
        Exp=int(round(SubExp/DayCostThisLevel/ComplexFightsPerDay))
        if level>=20:
            Exp=int(round(Exp*25.0/(level+5)))
        # 银币
        Hero_q,Equipment_q=1.10863085513201,1.11728462700911 #花费递增比例
        SilverBonus=200 #前期银币补偿（对前期比较重要，对后期影响可以忽略）
        HeroCostThisLevel=round(200*Hero_q**(level-1))*4 #本等级升级4个将领英雄的花费总数
        EquipmentCostThisLevel=round(120*Equipment_q**(level-1)*(98.9-0.9*level)/98.0)*2*4 #本等级强化2套蓝装的花费总数（假设100%成功，即最小消耗）
        TotalCostThisLevel=HeroCostThisLevel+EquipmentCostThisLevel #本等级升级英雄+强化装备的总花费
        Silver=int(round(TotalCostThisLevel/WarmupFightsPerDay)+SilverBonus)
    else:
        Exp,Silver=0,0
    return {'Exp':Exp,'Silver':Silver}

# 计算单场热身赛战斗银币奖励
def calc_warmup_fight(AttackerLevel,TeamPowerAttacker,TeamPowerDefender,is_win):
    """
    AttackerLevel=发起战斗的玩家等级
    TeamPowerAttacker=发起战斗的玩家队伍总战力
    TeamPowerDefender=被攻击方玩家退伍总战力
    is_win=是否获胜（失败无奖励）
    """
    SilverMultiplyFactor=(TeamPowerAttacker*1.0)/(TeamPowerDefender*1.0) #银币奖励乘算因子
    RandomMultiplyFactor=(5.0-math.sqrt(9.0-8.0*random.random()))/2.0 #随机浮动因子（1-2）
    # 如果大于70级，则按照70级的奖励计算
    if AttackerLevel>=70:
        AttackerLevel=70
    BasicSilver=BasicAward(AttackerLevel)['Silver'] #基础银币奖励
    LevelFactor=1.0-17.0/20.0*((AttackerLevel-1)/99.0)**8 #等级衰减因子
    WarmUpBonus=1200 #热身赛固有奖励加成
    # 最终奖励
    WarmupFightSilver=int(round(BasicSilver/SilverMultiplyFactor*RandomMultiplyFactor*LevelFactor+WarmUpBonus))
    if is_win:
        return WarmupFightSilver
    else:
        return 0

# 计算单场副本战斗经验奖励
def calc_complex_fight(ComplexLevel):
    """
    ComplexLevel=副本等级
    """
    #经验
    return BasicAward(ComplexLevel)['Exp']

# 计算单场势力战经验奖励
def calc_influence_fight(AttackerLevel,DefenderLevel,winScore):
    """
    AttackerLevel=进攻方玩家等级
    DefenderLevel=防守方玩家等级
    winScore=结算时，进攻方玩家已然胜场累计数目
    """
    N=10 #极限战斗总奖励与第一场奖励的比值
    LevelMultiplyFactor=2.0/(1.0+1.1**(AttackerLevel-DefenderLevel)) #等级差乘算因子
    ScoreMultiplyFactor=(1.0-1.0/N)**(winScore-1) #得分积累乘算因子
    InfluenceFightMyltiplyFactor=3.0 #势力战乘算因子
    InfluenceFightExp=int(round(BasicAward(AttackerLevel)['Exp']*LevelMultiplyFactor*ScoreMultiplyFactor*InfluenceFightMyltiplyFactor))
    return InfluenceFightExp




if __name__ == "__main__":
    hero_attr = [{'a':100,'b':100,'c':100,'d':100,'e':100},{'a':200,'b':200,'c':200,'d':200,'e':200}]
    avatar_church_exp = 1000
    church_exp = 1000
    calculate_fighting_points([0]*8,[0]*8,1,[16,10,10,11,1,10,10,10],[0]*8,1)
    #print get_avatar_church_attr(hero_attr,avatar_church_exp,church_exp)
