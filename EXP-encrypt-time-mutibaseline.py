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
    return timer.get_elapsed_time(testBatch)
    # print(str(testBatch)+" 个文件加密总耗时：" + str(timer.get_elapsed_time(testBatch)))


def exp_3DES_encrypt_oneFile(data):
    timer=tool.Timer()
    timer.start(1)
    while True:
        try:
            key = DES3.adjust_key_parity(get_random_bytes(24))
            break
        except ValueError:
            pass
    plaintext=data.encode()
    cipher = DES3.new(key, DES3.MODE_CFB)
    iv=cipher.iv
    ciphertxt=cipher.encrypt(plaintext)
    #完成加密，接下来解密
    timer.stop(1)
    return ciphertxt,iv,timer.get_elapsed_time(1)

def exp_3DES_encrypt_allFiles():
    # 控制循环
    count=0
    interval=400
    testBatch=8000
    #统计结果
    re=[]
    t=0
    for dirpath, dirnames, filenames in os.walk("dataset1"):
        for filename in filenames:
            #打开文件
            io=tool.IO_worker()
            data=io.read(os.path.join(dirpath,filename))
            count = count + 1

            #处理每个文件夹里的数据
            _,_,temp_t=exp_3DES_encrypt_oneFile(data)
            t=t+temp_t

            if int(count/interval)>int((count-1)/interval):
                re.append((int(count/interval)*interval,t))
                print(re)

            if count>testBatch:
                break
        if count>testBatch:
            break

    return
    # print(str(testBatch)+" 个文件加密总耗时：" + str(timer.get_elapsed_time(testBatch)))
def exp_AES_encrypt_oneFile(data):
    #先加密，测试相关参数
    timer = tool.Timer()
    timer.start(1)
    aes_key = get_random_bytes(16)
    ss=data.encode()
    cipher = AES.new(aes_key, AES.MODE_OCB)
    ciphertext, tag = cipher.encrypt_and_digest(ss)
    assert len(cipher.nonce) == 15
    timer.stop(1)
    return ciphertext,tag,timer.get_elapsed_time(1)

def exp_AES_encrypt_allFiles():
    # 控制循环
    count=0
    interval=400
    testBatch=8000
    #统计结果
    re=[]
    t=0
    for dirpath, dirnames, filenames in os.walk("dataset1"):
        for filename in filenames:
            #打开文件
            io=tool.IO_worker()
            data=io.read(os.path.join(dirpath,filename))
            count = count + 1

            #处理每个文件夹里的数据
            _,_,temp_t=exp_AES_encrypt_oneFile(data)
            t=t+temp_t

            if int(count/interval)>int((count-1)/interval):
                re.append((int(count/interval)*interval,t))
                print(re)

            if count>testBatch:
                break
        if count>testBatch:
            break

    return

def sibtitute_aChar(char,blinder):
    c = str(char)
    c_gbk = c.encode("gbk")
    return  (int.from_bytes(c_gbk, byteorder='big')+blinder)%CHAR_UP_BOUND

def exp_BlotSM_encrypt_allFiles():
    seed=time.time()
    random.seed(seed)
    # 控制循环
    timer=tool.Timer()
    count=0
    interval=400
    testBatch=8000
    #统计结果
    re=[]
    cipText=[]
    for dirpath, dirnames, filenames in os.walk("dataset1"):
        for filename in filenames:
            #打开文件
            io=tool.IO_worker()
            data=io.read(os.path.join(dirpath,filename))
            count = count + 1

            #处理每个文件夹里的数据
            timer.start(1)
            for i in data:
                cipText.append(sibtitute_aChar(i,random.randint(0,CHAR_UP_BOUND)))
            timer.stop(1)

            if int(count/interval)>int((count-1)/interval):
                re.append((int(count/interval)*interval,timer.get_elapsed_time(1)))
                print(re)

            if count>testBatch:
                break
        if count>testBatch:
            break

    return

def exp_OTP_encrypt_allFiles():
    seed=time.time()
    random.seed(seed)
    keys=[]
    # 控制循环
    timer=tool.Timer()
    count=0
    interval=400
    testBatch=8000
    #统计结果
    re=[]
    cipText=[]
    for dirpath, dirnames, filenames in os.walk("dataset1"):
        for filename in filenames:
            #打开文件
            io=tool.IO_worker()
            data=io.read(os.path.join(dirpath,filename))
            count = count + 1

            for j in range(len(data)):
                keys.append(random.randint(0,CHAR_UP_BOUND))

            #处理每个文件夹里的数据
            timer.start(1)
            for i in data:
                cipText.append(sibtitute_aChar(i,keys.pop()))
            timer.stop(1)

            if int(count/interval)>int((count-1)/interval):
                re.append((int(count/interval)*interval,timer.get_elapsed_time(1)))
                print(re)

            if count>testBatch:
                break
        if count>testBatch:
            break

    return

def exp_PSC3_encrypt_allFiles():
    seed=time.time()
    random.seed(seed)
    keys=[]
    table1=[]
    table2=[]
    table3=[]
    # 控制循环
    timer=tool.Timer()
    count=0
    interval=400
    testBatch=8000
    #统计结果
    re=[]
    cipText=[]
    for dirpath, dirnames, filenames in os.walk("dataset1"):
        for filename in filenames:
            #打开文件
            io=tool.IO_worker()
            data=io.read(os.path.join(dirpath,filename))
            count = count + 1

            keyLen=0
            while keyLen*keyLen*keyLen<len(data):
                keyLen=keyLen+1

            timer.start(1)
            for j in range(keyLen):
                table1.append(random.randint(0,CHAR_UP_BOUND))
                table2.append(random.randint(0,CHAR_UP_BOUND))
                table3.append(random.randint(0,CHAR_UP_BOUND))


            for i in table1:
                if len(data) == 0:
                    break
                for j in table2:
                    if len(data) == 0:
                        break
                    for k in table3:
                        if len(data)==0:
                            break
                        cipText.append(sibtitute_aChar(data[0],(i+j+k)%CHAR_UP_BOUND))
                        data=data[1:]
            timer.stop(1)

            if int(count/interval)>int((count-1)/interval):
                re.append((int(count/interval)*interval,timer.get_elapsed_time(1)))
                print(re)

            if count>testBatch:
                break
        if count>testBatch:
            break

    return

def exp_PSC4_encrypt_allFiles():
    seed=time.time()
    random.seed(seed)
    table1=[]
    table2=[]
    table3=[]
    table4=[]
    # 控制循环
    timer=tool.Timer()
    count=0
    interval=400
    testBatch=8000
    #统计结果
    re=[]
    cipText=[]
    for dirpath, dirnames, filenames in os.walk("dataset1"):
        for filename in filenames:
            #打开文件
            io=tool.IO_worker()
            data=io.read(os.path.join(dirpath,filename))
            count = count + 1

            keyLen=0
            while keyLen*keyLen*keyLen*keyLen<len(data):
                keyLen=keyLen+1

            timer.start(1)
            for j in range(keyLen):
                table1.append(random.randint(0,CHAR_UP_BOUND))
                table2.append(random.randint(0,CHAR_UP_BOUND))
                table3.append(random.randint(0,CHAR_UP_BOUND))
                table4.append(random.randint(0,CHAR_UP_BOUND))


            for i in table1:
                if len(data) == 0:
                    break
                for j in table2:
                    if len(data) == 0:
                        break
                    for k in table3:
                        if len(data)==0:
                            break
                        for ii in table4:
                            if len(data) == 0:
                                break
                            cipText.append(sibtitute_aChar(data[0],(i+j+k+ii)%CHAR_UP_BOUND))
                            data=data[1:]
            timer.stop(1)

            if int(count/interval)>int((count-1)/interval):
                re.append((int(count/interval)*interval,timer.get_elapsed_time(1)))
                print(re)

            if count>testBatch:
                break
        if count>testBatch:
            break

    return

def exp_PSC5_encrypt_allFiles():
    seed=time.time()
    random.seed(seed)
    table1=[]
    table2=[]
    table3=[]
    table4=[]
    table5=[]
    # 控制循环
    timer=tool.Timer()
    count=0
    interval=400
    testBatch=8000
    #统计结果
    re=[]
    cipText=[]
    for dirpath, dirnames, filenames in os.walk("dataset1"):
        for filename in filenames:
            #打开文件
            io=tool.IO_worker()
            data=io.read(os.path.join(dirpath,filename))
            count = count + 1

            keyLen=0
            while keyLen*keyLen*keyLen*keyLen*keyLen<len(data):
                keyLen=keyLen+1

            timer.start(1)
            for j in range(keyLen):
                table1.append(random.randint(0,CHAR_UP_BOUND))
                table2.append(random.randint(0,CHAR_UP_BOUND))
                table3.append(random.randint(0,CHAR_UP_BOUND))
                table4.append(random.randint(0,CHAR_UP_BOUND))
                table5.append(random.randint(0,CHAR_UP_BOUND))


            for i in table1:
                if len(data) == 0:
                    break
                for j in table2:
                    if len(data) == 0:
                        break
                    for k in table3:
                        if len(data)==0:
                            break
                        for ii in table4:
                            if len(data) == 0:
                                break
                            for jj in table5:
                                if len(data) == 0:
                                    break
                                cipText.append(sibtitute_aChar(data[0],(i+j+k+ii+jj)%CHAR_UP_BOUND))
                                data=data[1:]
            timer.stop(1)

            if int(count/interval)>int((count-1)/interval):
                re.append((int(count/interval)*interval,timer.get_elapsed_time(1)))
                print(re)

            if count>testBatch:
                break
        if count>testBatch:
            break

    return
