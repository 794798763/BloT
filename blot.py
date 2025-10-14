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

import tool
import hashlib
import random
import VectorCommitment
import sequitur2

ENCODE_UP_BOUND = 0xffffff
CHAR_UP_BOUND=0xffff


# print(sequitur.run_sequitur_in_dic("asdfhfghjfghdfghsdfgedfhrtehdfhgdfhfgh"))
# redic=sequitur.run_sequitur_in_dic("asdfhfghjfghdfghsdfgedfhrtehdfhgdfhfgh")

# io=tool.IO_worker()
# io.write_rulesDic_to_json(redic,"testjson.json")
# newjson=io.read_rulesDic_from_jsonfile('./result/testjson.json')
def generateMaskSeedsDict(codedRulesDict):
    maskSeedsDict=dict()
    for i,_ in codedRulesDict.items():
        maskSeedsDict[i]="".join(random.choice("qwertyuiksdfghjklzxcvbnm123456789") for _ in range(8))
    return maskSeedsDict

def extractionLayer(filepath,timer):
    graphSize=1024*1024 #1mb
    seq = sequitur2.Sequitur2()
    with open(filepath,'r') as file:
        count=0
        while True:
            newString=file.read(graphSize)
            if not newString:
                break
            newString=newString.replace('/',"")
            timer.start('extractionLayer')
            seq.run_new_string(newString)
            timer.stop('extractionLayer')
            print("new graph "+str(count)+" success")
            count=count+1
    seq.wash_rules_by_usage()
    return seq.get_rules_in_dict()



def encodingLayer(rulesDict,timer):
    codedRulesDict=dict()
    for key,vlist in rulesDict.items():
        templist=[]
        timer.start("encodingLayer")
        for v in vlist:
            if isRule(v):
                templist.append(encodeRULES(v))
                continue
            else:
                templist.append(encodeCHAR(v))
        timer.stop("encodingLayer")
        codedRulesDict[key]=templist
        rulesDict[key]=[]
    return codedRulesDict

def substitutionLayer(codedRulesDict,timer):
    maskSeedDcit=generateMaskSeedsDict(codedRulesDict)
    confidentialRulesDict=dict()
    timer.start("substitutionLayer")
    for key,vlist in codedRulesDict.items():
        confidentialRulesDict[key]=substitute_a_rules(vlist,maskSeedDcit[key])
        codedRulesDict[key]=[]
    timer.stop("substitutionLayer")
    return confidentialRulesDict,maskSeedDcit


def encodeRULES(ruleKey):
    ruleKey=str(ruleKey)
    rule=ruleKey.replace("R","")
    ruleNum=int(rule)
    global CHAR_UP_BOUND
    global ENCODE_UP_BOUND
    if ruleNum>ENCODE_UP_BOUND-CHAR_UP_BOUND:
        print("rules数量越界")
        return
    return ruleNum+CHAR_UP_BOUND+1

def encodeCHAR(c):
    c=str(c)
    c_gbk=c.encode("gbk")
    return int.from_bytes(c_gbk,byteorder='big')

def decompress_maskSeed_to_mask(seedStr,ruleLength):
    global ENCODE_UP_BOUND
    #生成每一个rule的Maskseed
    h=hashlib.sha256(seedStr.encode('utf-8'))
    h_hex=h.hexdigest()
    seed=int(h_hex,16)%ENCODE_UP_BOUND
    #生成mask
    random.seed(seed)
    mask=[]
    for i in range(ruleLength):
        mask.append(random.randint(0,ENCODE_UP_BOUND))
    return mask

def substitute_a_rules(codedCharList,seedStr):
    global ENCODE_UP_BOUND
    mask=decompress_maskSeed_to_mask(seedStr,len(codedCharList))
    #把rules里字符的编码全部带换掉
    confidentialRule=[]
    for i,codedChar in enumerate(codedCharList):
        confidentialRule.append((codedChar+mask[i])%ENCODE_UP_BOUND)
    return confidentialRule

def recover_a_rule(seedStr,confidentialRule):
    global ENCODE_UP_BOUND
    codedCharList=[]
    mask = decompress_maskSeed_to_mask(seedStr, len(confidentialRule))
    for i,j in enumerate(confidentialRule):
        codedCharList.append((ENCODE_UP_BOUND+int(j)-mask[i])%ENCODE_UP_BOUND)
    return codedCharList



def isRule(s):
    if not len(s)>1:
        return False
    if not s[0]=='R':
        return False
    return True


#main方法
def Encrypt(filepath):
    return

def testEncrypt():
    text="asdfhfghjfghdfghsdfgedfhrtehdfhgdfhfgh"
    text=extractionLayer(text)
    print(text)
    print("****************************************************************")
    text=encodingLayer(text)
    print(text)
    print("------------------------------------------------------------------")


#####################
def generateADS(code2ruleDict,rule2seedDict):
    global CHAR_UP_BOUND
    proofsDict=dict()
    relayNode_vectorComDict=dict()
    relayNode_hashDict=dict()
    codeOfR0=CHAR_UP_BOUND+1
    getRelayNodeHash(codeOfR0,code2ruleDict,rule2seedDict,relayNode_hashDict,relayNode_vectorComDict,proofsDict)
    return relayNode_hashDict,relayNode_vectorComDict,proofsDict


################relaynode的hash是以整数形式存在
def getRelayNodeHash(ruleCode,code2ruleDict,rule2seedDict,relayNode_hashDict,relayNode_vectorComDict,proofsDict):
    if ruleCode in relayNode_hashDict.keys():
        return relayNode_hashDict[ruleCode]
    if ruleCode not in code2ruleDict.keys():
        return ruleCode
    #确定是一个没求过hash的rule，开始求他的hash
    codedRuleList = code2ruleDict[ruleCode]
    msg_list=[]
    for subRule in codedRuleList:
        h = getRelayNodeHash(subRule, code2ruleDict, rule2seedDict, relayNode_hashDict, relayNode_vectorComDict,proofsDict)
        msg_list.append(h)
    n, e, a, S = VectorCommitment.keygen(msg_list, 32)
    c = VectorCommitment.commit(msg_list, S, n)
    relayNode_vectorComDict[ruleCode]=c
    templist = []
    for i in range(len(msg_list)):
        proof = VectorCommitment.open(msg_list, e, a, n, i)
        templist.append((msg_list[i], proof, S, e, n))
    proofsDict[ruleCode]=templist
    temp1=hashlib.sha256(str(rule2seedDict[ruleCode]).encode("utf-8")).hexdigest()
    temp2=hashlib.sha256(str(c).encode("utf-8")).hexdigest()
    ruleHashStr=hashlib.sha256(str(temp1+temp2).encode("utf-8")).hexdigest()
    hashFinal=int(ruleHashStr[-8:],16)
    relayNode_hashDict[ruleCode]=hashFinal
    return hashFinal


def test():
    messages = [0x132,0x4896,0x46,0x89654]  # create some messages
    n, e, a, S = VectorCommitment.keygen(messages, 12)  # generate public parameters, 3 is max number of bits
    #生成消息的承诺，要传入完整消息
    c = VectorCommitment.commit(messages, S, n)  # generate commitment
    print(hex(c))
    print("---------------------------------------")
    #生成数据的位置证明
    proof = VectorCommitment.open(messages, e, a, n, 1)  # create opening (proof)
    print(hex(proof))
    print("*****************************************")
    #e,n，a，S是公共参数，None是完整数据，不需要提供，
    #proof是证明，c是承诺，mess[]是具体消息，0...1是位置
    timer=tool.Timer()
    timer.start(1)
    for i in range(100):
        VectorCommitment.verify(c, messages[1], 1, proof, S, None, e, n)
    timer.stop(1)
    print(timer.get_elapsed_time_in_ms(1))
    timer.start(2)
    a=0
    for i in range(100):
        a=hash("hsuidfsdiofhsdoifhosdhfsdhfjkhsdjkfhsjkdhfksjdhfkjhsdfkjhsdjkfhsjkdhfkjshdfjkhsdfkjhsdkjfhsdkjfhkjsdhfkjsdhfkjhsdkjhfkhjdfhskdjfh")
    print(hex(a))
    timer.stop(2)
    print(timer.get_elapsed_time_in_ms(2))
# ruleHashStr=hashlib.sha256("0x654a516b489e12f312d489".encode("utf-8")).hexdigest()
# print(ruleHashStr)
# hashFinal=int(ruleHashStr[-8:],16)
# print(hashFinal)
