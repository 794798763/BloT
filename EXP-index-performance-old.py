import os
import sys
import tool
import blot
import sequitur2
import blot
import tool
import index
import sequitur
import sys
import time
import  random

from Crypto.Cipher import AES
from Crypto.Cipher import DES3
from Crypto.Hash import HMAC, SHA256
from Crypto.Random import get_random_bytes
CHAR_UP_BOUND=0xffff

def exp_CFG_extraction(path):
    DATASET="HDFS"
    seq = sequitur2.Sequitur2()
    line_count=0
    with open(path,"r") as file:
        while True:
            line = file.readline()
            if not line:  # 读到文件末尾返回空字符串
                break
            seq.run_new_string(line)
            line_count=line_count+1
            print("成功处理行数"+str(line_count))
    seq.wash_rules_by_usage()
    print("成功清洗，正在准备调整输出格式")
    cfg = seq.get_rules_in_dict()

    char_count=0
    for rule in cfg:
        char_count=char_count+1+len(rule)
    print("字符总数为  "+str(char_count))

    io=tool.IO_worker()
    io.write_Dic_to_Jsonfile(cfg,DATASET+"-cfg.json")

def count_char_num(path):
    count=0
    with open(path,"r") as file:
        while True:
            line = file.readline()
            if not line:  # 读到文件末尾返回空字符串
                break
            count=count+len(line)
    print("共含有字符数： "+str(count))

def exp_blot_encrypt(path):
    # 控制循环
    count=0
    #统计结果
    timer=tool.Timer()
    seq = sequitur2.Sequitur2()
    for dirpath, dirnames, filenames in os.walk("dataset1"):
        for filename in filenames:
            #打开文件
            io=tool.IO_worker()
            data=io.read(os.path.join(dirpath,filename))
            count = count + 1

            #处理每个文件夹里的数据
            newString = data.replace('/', "")
            seq.run_new_string(newString)
            if count>testBatch:
                break
        if count>testBatch:
            break
    seq.wash_rules_by_usage()
    CFG=seq.get_rules_in_dict()
    #清理内存
    del seq
    timer.start(testBatch)
    codedCFG=blot.encodingLayer(CFG,timer)
    timer.stop(testBatch)
    del CFG
    timer.start(testBatch)
    blot.substitutionLayer(codedCFG,timer)
    timer.stop(testBatch)
    # print(str(testBatch)+"  的总耗时是  "+ str(timer.get_elapsed_time(testBatch)))
    return {"encodingLayer":timer.get_elapsed_time("encodingLayer"),"substitutionLayer":timer.get_elapsed_time("substitutionLayer")}
    # print(str(testBatch)+" 个文件加密总耗时：" + str(timer.get_elapsed_time(testBatch)))

def construct_index(cfg_path):
    io=tool.IO_worker()
    cfg=io.read_Dic_from_Jsonfile(cfg_path)
    timer=tool.Timer()
    timer.start("ruleindex")
    ri=index.construct_ruleindex(cfg)
    timer.stop("ruleindex")
    timer.start("stepindex")
    si=index.construct_stepindex(ri)
    timer.stop("stepindex")
    io.write_Dic_to_Jsonfile(index.get_ruleindex(ri),"BGL-ruleindex.json")
    io.write_Dic_to_Jsonfile(index.get_stepindex(si),"BGL-stepindex.json")
    print("ruleindex的构造耗时是：  "+str(timer.get_elapsed_time("ruleindex")))
    print("stepindex的构造耗时是：  "+str(timer.get_elapsed_time("stepindex")))
construct_index("./result/BGL-cfg.json")
