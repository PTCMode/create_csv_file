#!/usr/bin/python3

import os
import sys
import random
import getopt
import multiprocessing
import threading
import platform
import time

import config
import func


def usage():
    print('==================== help ====================')
    print('Nothing here now.')
    print('==================== end  ====================')


class craete:
    'craete csv data by ordered value.'

    def __init__(self, execOptList):
        # TODO: 下方三个列表合并成一个类来管理
        # 线程对象列表
        self.threadList = []
        # 文件路径列表
        self.fileList = []
        # 列生成类对象列表
        self.colList = []
        # 生成行数
        self.rowCount = int(1)
        # 生成列数
        self.colCount = int(1)
        # 配置选项信息
        self.execOptList = execOptList
        # 选择初始化方式
        if (self.execOptList.usingConfig):
            self.init_by_conf()
        else:
            self.init_by_user()

    def init_by_conf(self):
        print('==================== init_by_conf ====================')
        print('读取 config.py 文件')
        config.colCount = len(config.colInfoList)
        if (len(config.colInfoList) != config.colCount):
            print('请检查 config.py 文件格式')
            sys.exit()
        if (config.rowCount <= 0):
            sys.exit()
        if self.execOptList.threadCount > config.rowCount:
            print("线程数大于总行数")
            sys.exit()
        self.rowCount = config.rowCount
        for colInfoIdx in range(len(config.colInfoList)):
            print('\n生成第 %d 列信息:' % (colInfoIdx + 1))
            print('  - 第 %d 列类型: %s\n  - 第 %d 列数据设置: ' % ( \
                    colInfoIdx + 1, config.colInfoList[colInfoIdx][0], colInfoIdx + 1), end = '')
            if isinstance(config.colInfoList[colInfoIdx][1], list):
                print(' | '.join(map(str, config.colInfoList[colInfoIdx][1])))
            else:
                print(config.colInfoList[colInfoIdx][1])

            curCol = self.execOptList.create_col(config.colInfoList[colInfoIdx])
            if (curCol == None):
                print('请检查 config.py 文件格式')
                sys.exit()
            self.colList.append(curCol)

    # TODO: 修改更新手动初始化逻辑
    def init_by_user(self):
        print('==================== init_by_user ====================')
        self.colCount = int(input('请输入生成列数: '))
        self.rowCount = int(input('\n请输入生成行数: '))
        if self.execOptList.threadCount > self.rowCount:
            print("线程数大于总行数")
            sys.exit()
        print('')
        #
        index = 1
        while (index <= self.colCount):
            print('生成第 %d 列信息:' % (index))
            str = input('  - 第 %d 列类型: ' % (index))
            val = int(input('  - 第 %d 列起始数据(int): ' % (index)))
            curCol = self.execOptList.create_col([str, val])
            if (curCol == None):
                print('列类型非法, 请重新输入')
                continue
            self.colList.append(curCol)

            index += 1

    def write_to_file(self, file, val):
        file.write(val)

    # TODO: 有些乱, 按逻辑拆分为几个函数
    def main(self):
        print('\n==================== main ====================')
        filePath = self.execOptList.filePath + '.' + str(self.execOptList.rand)
        # 创建进程
        bigen = 0
        end = 0
        for threadIdx in range(self.execOptList.threadCount):
            end += self.rowCount // self.execOptList.threadCount
            if end > self.rowCount or threadIdx == self.execOptList.threadCount - 1:
                end = self.rowCount
            self.fileList.append((filePath + '.' + str(threadIdx)))
            if platform.architecture()[1] == 'ELF':
                self.threadList.append(multiprocessing.Process( \
                        target = self.process, \
                        daemon = True, \
                        args = [bigen, end, threadIdx]))
            elif platform.architecture()[1] == 'WindowsPE':
                self.threadList.append(threading.Thread( \
                        target = self.process, \
                        daemon = True, \
                        args = [bigen, end, threadIdx]))
            else:
                sys.exit()
            self.threadList[threadIdx].start()
            print('\r  + 进程 %d / %d 开始' % (threadIdx + 1, self.execOptList.threadCount), end = '')
            bigen = end
        print('')
        # 等待进程结束
        for threadIdx in range(self.execOptList.threadCount):
            self.threadList[threadIdx].join()
            print('\r  - 进程 %d / %d 结束' % (threadIdx + 1, self.execOptList.threadCount), end = '')
        # 合并文件
        if (self.execOptList.needMergeFiles):
            print('\n==================== marging ====================')
            for threadIdx in range(self.execOptList.threadCount):
                print('\r  - 正在合并第 %d / %d 份文件' % (threadIdx + 1, self.execOptList.threadCount), end = '')
                # 判断系统类型, 选择不同合并方式
                if platform.architecture()[1] == 'ELF':
                    # 如果系统为Linux, 使用cat, 速度快
                    command = str('cat ' + self.fileList[threadIdx] + ' >> ' + self.execOptList.filePath)
                    os.system(command)
                else:
                    # 否则使用python, 速度慢
                    with open(self.execOptList.filePath, mode = 'a', encoding = 'utf-8', newline='\n') as file:
                        for line in open(self.fileList[threadIdx], encoding = 'utf-8', newline='\n'):
                            file.writelines(line)
                os.remove(self.fileList[threadIdx])
        # 打乱文件行
        # TODO: 优化进度更新逻辑
        if self.execOptList.needShufFiles:
            print('\n\n==================== shuffling ====================')
            print('  - 正在打乱文件')
            tmp_file = self.execOptList.filePath + '.' + str(self.execOptList.rand) + '.upset'
            readCount = 0
            writeCount = 0
            out = open(tmp_file, mode = 'w', encoding = 'utf-8', newline='\n')
            lines=[]
            curTime = time.time()
            preTime = float(0)
            with open(self.execOptList.filePath, mode = 'r', encoding = 'utf-8', newline='\n') as infile:
                for line in infile:
                    readCount += 1
                    if preTime < curTime + 5:
                        preTime = curTime
                        print('\r    - 读取文件: %.2a' % (float(readCount) / self.rowCount), end = '')
                    lines.append(line)
            print('\r    - 读取文件: 100.00%', end = '')
            random.shuffle(lines)
            print('')

            curTime = time.time()
            preTime = float(0)
            for line in lines:
                writeCount += 1
                if preTime < curTime + 5:
                    preTime = curTime
                    print('\r    - 写入文件: %.2a' % (float(writeCount) / self.rowCount), end = '')
                out.write(line)
            print('\r    - 写入文件: 100.00%', end = '')
            out.close()
            os.remove(self.execOptList.filePath)
            os.rename(tmp_file, self.execOptList.filePath)
        print('\n\n==================== work all over ====================')


    def process(self, bigen, end, threadIdx):
        random.seed(self.execOptList.seed + threadIdx)
        with open(self.fileList[threadIdx], mode = 'x', encoding = 'utf-8', newline='\n') as file:
            curStr = str()
            for index in range(bigen, end):
                curStr = ''
                curStr += self.colList[0].next(index)
                for colidx in range(1, len(self.colList)):
                    curStr += self.execOptList.separator
                    curStr += self.colList[colidx].next(index)
                curStr += '\n'
                self.write_to_file(file, curStr)

if __name__ == '__main__':
    # info
    print('\ncreate_csv_file v0.1.1\n')

    # os spportition
    if platform.architecture()[1] == 'ELF':
        pass
    elif platform.architecture()[1] == 'WindowsPE':
        multiprocessing.freeze_support()
    else:
        print('不确定这个系统有啥坑, 先不支持\n')
        sys.exit()

    # getopt
    execOptList = func.execOpt()
    execOptList.seed = execOptList.rand
    random.seed(int(execOptList.seed))
    print('当前随机数种子为: %s\n' % execOptList.rand)
    options, args = getopt.getopt(sys.argv[1:], \
            "hcmj:o:s:S:r", ["help", "use-config", "marge", "cpu=", "output=", "seed=", "separator=", "shuf"])
    try:
        options, args = getopt.getopt(sys.argv[1:], \
                "hcmj:o:s:S:r", ["help", "use-config", "marge", "cpu=", "output=", "seed=", "separator=", "shuf"])
    except getopt.GetoptError:
        sys.exit()
    for name, value in options:
        if name in ("-h", "--help"):
            usage()
            sys.exit()
        elif name in ("-c", "--use-config"):
            execOptList.usingConfig = True
        elif name in ("-m", "--marge"):
            execOptList.needMergeFiles = True
        elif name in ("-j", "--cpu"):
            if platform.architecture()[1] == 'ELF':
                execOptList.threadCount = int(value)
            elif platform.architecture()[1] == 'WindowsPE':
                print('Windows系统暂时不支持多核\n')
                execOptList.threadCount = int(1)
                multiprocessing.freeze_support()
        elif name in ("-o", "--output"):
            execOptList.filePath = value
        elif name in ("-s", "--seed"):
            execOptList.seed = int(value)
            random.seed(execOptList.seed)
            print('随机数种子设置为: %s\n' % value)
        elif name in ("-S", "--separator"):
            execOptList.separator = value
        elif name in ("-r", "--shuf"):
            execOptList.needMergeFiles = True
            execOptList.needShufFiles = True
        else:
            usage()
            sys.exit()


    # main
    main_process = craete(execOptList)
    main_process.main()

