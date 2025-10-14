import os
import sys
import tool
import blot
import sequitur2
import blot
import tool
import sequitur
import sys
import time
import  random

from Crypto.Cipher import AES
from Crypto.Cipher import DES3
from Crypto.Hash import HMAC, SHA256
from Crypto.Random import get_random_bytes
CHAR_UP_BOUND=0xffff
def exp_blot_encrypt_oneInterval(testBatch):
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
re=dict()
re[1000]=exp_blot_encrypt_oneInterval(1000)
print(re)
re[2000]=exp_blot_encrypt_oneInterval(2000)
print(re)
re[3000]=exp_blot_encrypt_oneInterval(3000)
print(re)
re[4000]=exp_blot_encrypt_oneInterval(4000)
print(re)
re[5000]=exp_blot_encrypt_oneInterval(5000)
print(re)