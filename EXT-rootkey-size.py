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

def exp_PSC_keysize():
    char_num=0
    count=0
    testBatch=5000

    interval=1000
    for dirpath, dirnames, filenames in os.walk("dataset1"):
        for filename in filenames:
            #打开文件
            io=tool.IO_worker()
            data=io.read(os.path.join(dirpath,filename))
            count = count + 1
            char_num=char_num+len(data)

            if int(count/interval)>int((count-1)/interval):
                tablesize=0
                while tablesize*tablesize*tablesize*tablesize*tablesize<char_num:
                    tablesize=tablesize+1
                print(char_num)
                print(tablesize*5*3/1024)

            if count>testBatch:
                break
        if count>testBatch:
            break

    return
exp_PSC_keysize()