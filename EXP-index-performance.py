import tool
import IFSI
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

BatchSize = 1000000
stepsize=10000
DATASET = "HDFS"
def safe_pop(l):
    try:
        return l.pop()
    except IndexError:
        return None

def exp_CFG_extraction_in_batch(path):

    seq = sequitur2.Sequitur2()
    with open(path,"r", encoding='utf-8') as file:
        data=file.read(BatchSize)
        print(len(data))
        seq.run_new_string(data)
    seq.wash_rules_by_usage()
    print("成功清洗，正在准备调整输出格式")
    cfg = seq.get_rules_in_dict()
    cfg=seq.resort(cfg)

    char_count=0
    for rule in cfg:
        char_count=char_count+1+len(rule)
    print("字符总数为  "+str(char_count))

    io=tool.IO_worker()
    io.write_Dic_to_Jsonfile(cfg,DATASET+"-B0-cfg.json")

def construct_IFSI():
    io = tool.IO_worker()
    timer=tool.Timer()
    cfg = io.read_Dic_from_Jsonfile("./result/"+DATASET+"-B0-cfg.json")
    timer.start(1)
    si=IFSI.make_IFSI(cfg)
    timer.stop(1)
    print(timer.get_elapsed_time(1))
    io.write_Dic_to_Jsonfile(si,DATASET+"-B0-IFSI.json")

def access_a_char_by_isfi(ofset):
    io=tool.IO_worker()
    cfg=io.read_Dic_from_Jsonfile("./result/"+DATASET+"-B0-cfg.json")
    ifsi=io.read_Dic_from_Jsonfile("./result/"+DATASET+"-B0-IFSI.json")["result"]
    ofset_in_batch=ofset%BatchSize
    iter=int(ofset_in_batch/stepsize)
    count=iter*stepsize
    length=0
    stake=ifsi[iter]
    timer=tool.Timer()
    timer.start("index")
    while True:
        s = safe_pop(stake)
        if s is None:
            break
        rule_name=s[0]
        rule=cfg[rule_name]
        b=s[1]+1
        if b>len(rule):
            continue
        for char_pointer,char in enumerate(rule[b:]):
            length = length + 1
            if len(char) ==1:
                count=count+1
                if count==ofset_in_batch:
                    timer.stop("index")
                    return rule_name,char_pointer+b,timer.get_elapsed_time_in_ms("index"),length
            else:
                stake.append((rule_name,char_pointer+b))
                stake.append((char,-1))
                break
        # print("经过一条rule：" + str(rule_name))
    timer.stop("index")
    return None,None,timer.get_elapsed_time_in_ms("index"),length

# exp_CFG_extraction_in_batch("HDFS.txt")
# construct_IFSI()
def EXP_test_Blot_Access_mutlbaseline():
    l=[]
    total_index = 0
    total_OTK = 0
    length=0
    for i in range(100):
        o=random.randint(0,743184949)
        snr,snc,t,ll=access_a_char_by_isfi(o)
        re = dict()
        re["snr"]=snr
        re["snc"]=snc
        re["index"]=t
        total_index = total_index+t
        length=length+ll
        timer=tool.Timer()
        timer.start(2)
        for j in range(snc):
            random.randint(0,0xffffff)
        timer.stop(2)
        re["generateOTP"]=timer.get_elapsed_time_in_ms(2)
        total_OTK=total_OTK+timer.get_elapsed_time_in_ms(2)
        re["time(ms)"]=t+timer.get_elapsed_time_in_ms(2)
        l.append(re)
    print(total_index/100)
    print(length/100)
    print(total_OTK/100)



def EXP_test_3DE_access():
    while True:
        try:
            key = DES3.adjust_key_parity(get_random_bytes(24))
            break
        except ValueError:
            pass
    # 加密
    io = tool.IO_worker()
    s = io.read(DATASET+".txt")
    print("读取完成")
    plaintext = s.encode()
    cipher = DES3.new(key, DES3.MODE_CFB)
    iv = cipher.iv
    print("密钥生成，开始加密")
    ciphertxt = cipher.encrypt(plaintext)
    print(sys.getsizeof(ciphertxt))
    # 完成加密，接下来解密
    print("完成加密，接下来解密")
    timer=tool.Timer()
    timer.start(1)
    cipher2 = DES3.new(key, DES3.MODE_CFB, iv=iv)
    try:
        message = cipher2.decrypt(ciphertxt)
        timer.stop(1)
        print(timer.get_elapsed_time(1))
    except ValueError:
        print("The message was modified!")
        sys.exit(1)


def EXP_blot_access_without_index(k):
    io=tool.IO_worker()
    cfg=io.read_Dic_from_Jsonfile("./result/"+DATASET+"-cfg.json")
    iter=int(960049/2)+k
    length=0
    count=0
    stake=[("R0",-1)]
    timer=tool.Timer()
    timer.start("index")
    while True:
        s = safe_pop(stake)
        if s is None:
            break
        rule_name=s[0]
        rule=cfg[rule_name]
        b=s[1]+1
        if b>len(rule):
            continue
        for char_pointer,char in enumerate(rule[b:]):
            length = length + 1
            if len(char) ==1:
                count=count+1
                if count==iter:
                    timer.stop("index")
                    return rule_name,char_pointer+b,timer.get_elapsed_time_in_ms("index"),length
            else:
                stake.append((rule_name,char_pointer+b))
                stake.append((char,-1))
                break
        # print("经过一条rule：" + str(rule_name))
    timer.stop("index")
    return None,None,timer.get_elapsed_time_in_ms("index"),length




# EXP_test_Blot_Access_mutlbaseline()
# EXP_test_3DE_access()

def EXP_blotSM_access():
    t=tool.Timer()
    t.start(1)
    for i in range(int(1566807277/2)):
        random.randint(0,0xffffff)
    t.stop(1)
    print(t.get_elapsed_time(1))

def EXP_AES_access():
    # 先加密，测试相关参数
    print("开始")
    io = tool.IO_worker()
    s = io.read(DATASET+".txt")
    data = s.encode()
    aes_key = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_OCB)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    print(sys.getsizeof(ciphertext))
    print("加密完成，开始解密")
    assert len(cipher.nonce) == 15
    # 再解密，测试相关参数
    timer=tool.Timer()
    timer.start(1)
    nonce = cipher.nonce
    cipher2 = AES.new(aes_key, AES.MODE_OCB, nonce=nonce)
    try:
        message = cipher2.decrypt_and_verify(ciphertext, tag)
        timer.stop(1)
        print(timer.get_elapsed_time(1))
    except ValueError:
        print("The message was modified!")
        sys.exit(1)

# exp_CFG_extraction_in_batch(DATASET+".txt")
construct_IFSI()