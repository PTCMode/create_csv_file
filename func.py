#!/usr/bin/python3

import time
import math
import random
import platform
import config


class execOpt:
    'execOpt'
    def __init__(self):
        # 设置 是否使用config 默认值
        self.usingConfig = bool(False)
        # 设置 是否合并多线程产生文件 默认值
        self.needMergeFiles = bool(False)
        # 设置 是否打乱文件内的行 默认值
        self.needShufFiles = bool(False)
        # 设置 默认线程数量
        self.threadCount = int(1)
        # 设置 默认文件路径
        if platform.architecture()[1] == 'ELF':
            self.filePath = str('./tmp_file')
        else:
            self.filePath = str('.\\tmp_file')
        # 设置 默认分隔符
        self.separator = str(';')
        # 生成 随机数 (系统时间基准)
        self.rand = int(str(time.time()).split(".")[-1])
        self.seed = int(-1)

    def create_col(self, array):
        if array[0].upper() == 'NULL':
            return null(array)
        elif array[0].upper() == 'INT' \
                or array[0].upper() == 'LONG' \
                or array[0].upper() == 'DOUBLE' \
                or array[0].upper() == 'NUMBER':
            return int_order(array)
        elif array[0].upper() == 'CHAR' \
                or array[0].upper() == 'VARCHAR':
            return char_order(array)
        elif array[0].upper() == 'DATE' \
                or array[0].upper() == 'TIMESTAMP':
            return date_order(array)
        elif array[0].upper() == 'YMINTERVAL' \
                or array[0].upper() == 'YM':
            return y2m_order(array)
        elif array[0].upper() == 'DSINTERVAL' \
                or array[0].upper() == 'DS':
            return d2s_order(array)
        if array[0].upper() == 'CUSTOM':
            return custom(array)
        else:
            return


class func:
    'parent class'

    def __init__(self, array:list):
        # 初始化成员变量
        self.val = array[1]
        if len(array) > 2 and type(array[2]) is int:
            self.step = array[2]
        else:
            self.step = 1
        print(self.step)
        self.optNumFuncVec = []
        self.optStrFuncVec = []
        self.keyArray = []
        # 解析特殊处理
        if len(array) > 2:
            for index in range(2, len(array)):
                if type(array[index]) is not list:
                    continue
                if array[index][0].upper() == 'LIMIT':
                    print(array[index])
                    limit_val = int(array[index][1])
                    self.optNumFuncVec.append(lambda dividend : dividend % limit_val)
                elif array[index][0].upper() == 'KEY':
                    print(array[index])
                    self.add_option_key(array[index])
                elif array[index][0].upper() == 'RANDOM':
                    print(array[index])
                    self.add_option_random(array[index])
                else:
                    pass
            for index in range(2, len(array)):
                if type(array[index]) is not list:
                    continue
                if array[index][0].upper() == 'EXLEN':
                    self.add_option_exlen(array[index])
                elif array[index][0].upper() == 'QUOTE':
                    pass
                else:
                    pass

    def add_option_key(self, optDesc:list):
        sum = 0
        tmp = 0
        if len(optDesc) > 2:
            for keyRateIdx in range(2, len(optDesc)):
                sum = sum + optDesc[keyRateIdx]
                if keyRateIdx < optDesc[1] + 2:
                    tmp = tmp + config.rowCount * optDesc[keyRateIdx]
                elif keyRateIdx == optDesc[1] + 2:
                    tmp = config.rowCount
                self.keyArray.append(math.floor(tmp))
                pass
        if len(optDesc) - 2 < optDesc[1]:
            rate = (1 - sum) / (optDesc[1] - len(optDesc) + 2)
            for keyRateIdx in range(len(optDesc) - 2, optDesc[1]):
                if keyRateIdx < optDesc[1] - 1:
                    tmp = tmp + config.rowCount * rate
                else:
                    tmp = config.rowCount
                self.keyArray.append(math.floor(tmp))
                pass
            pass
        # print(self.keyArray)

        def tmpFunc(val):
            for vecIdx in range(len(self.keyArray)):
                if val < self.keyArray[vecIdx]:
                    return vecIdx
            return

        self.optNumFuncVec.append(tmpFunc)
        pass

    def add_option_random(self, optDesc:list):

        def tmpFunc(val):
            return random.randint(0, optDesc[1] - 1)

        self.optNumFuncVec.append(tmpFunc)
        pass

    # TODO: 增加自定义字符串逻辑
    def add_option_exlen(self, optDesc:list):

        def tmpFunc(val:str):
            if type(optDesc[1]) is int:
                return val.rjust(optDesc[1], ' ')
            elif type(optDesc[1]) is list:
                if optDesc[1][0] == True and optDesc[1][1] == True:
                    return ''.join([random.choice(optDesc[1][2]) for i in range(random.randrange(0, optDesc[1][3] - len(val)))]) + val
                elif optDesc[1][0] == True and optDesc[1][1] == False:
                    return val.rjust(random.randrange(0, optDesc[1][3] - len(val)), optDesc[1][2][0])
                elif optDesc[1][0] == False and optDesc[1][1] == True:
                    return ''.join([random.choice(optDesc[1][2]) for i in range(optDesc[1][3] - len(val))]) + val
                else:
                    return val.rjust(optDesc[1][3], optDesc[1][2][0])
            else:
                exit()

        self.optStrFuncVec.append(tmpFunc)
        pass

class null(func):
    'null'
    def next(self, val:int):
        return ''

class int_order(func):
    'int_order'
    def next(self, val:int):
        tmp = val * self.step
        for optNumFunc in self.optNumFuncVec:
            tmp = optNumFunc(tmp)
        return str(self.val + tmp)

class char_order(func):
    'char_order'
    def next(self, val:int):
        tmp = val * self.step
        for optNumFunc in self.optNumFuncVec:
            tmp = optNumFunc(tmp)
        tmp = str(self.val + tmp)
        for optStrFunc in self.optStrFuncVec:
            tmp = optStrFunc(tmp)
        return str('\"' + tmp + '\"')

class date_order(func):
    'date_order'
    def next(self, val:int):
        tmp = val * self.step
        for optNumFunc in self.optNumFuncVec:
            tmp = optNumFunc(tmp)
        return time.strftime("\"%Y-%m-%d %H:%M:%S\"", time.localtime(self.val + tmp))

class y2m_order(func):
    'y2m_order'
    def next(self, val:int):
        tmp = val * self.step
        for optNumFunc in self.optNumFuncVec:
            tmp = optNumFunc(tmp)
        tmp = self.val + tmp
        return str('\"' + str((tmp) // 12) + '-' + str((tmp) % 12) + '\"')

class d2s_order(func):
    'd2s_order'
    def next(self, val:int):
        tmp = val * self.step
        for optNumFunc in self.optNumFuncVec:
            tmp = optNumFunc(tmp)
        tmp = self.val + tmp
        return str("\"" + str((tmp) // 86400) + time.strftime(" %H:%M:%S\"", time.localtime(tmp)))

class custom(func):
    'custom'
    def next(self, val:int):
        tmp = val * self.step
        for optNumFunc in self.optNumFuncVec:
            tmp = optNumFunc(tmp)
        tmp = self.val[tmp % len(self.val)]
        for optStrFunc in self.optStrFuncVec:
            tmp = optStrFunc(tmp)
        return str('\"' + tmp + '\"')

