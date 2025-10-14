import blot
import tool
import sequitur
import sys

from Crypto.Cipher import AES
from Crypto.Cipher import DES3
from Crypto.Hash import HMAC, SHA256
from Crypto.Random import get_random_bytes

def encrypt_a_string(s):
    rulesDict=blot.extractionLayer(s)
    print("****")
    codedRulesDict=blot.encodingLayer(rulesDict)
    print("----------")
    maskSeedsDict=blot.generateMaskSeedsDict(codedRulesDict)
    print("555555555555555555")
    confidentialRulesDict=blot.substitutionLayer(codedRulesDict, maskSeedsDict)
    return confidentialRulesDict

# encrypt_a_file('./NCBI.txt')
def encrypt_a_file(filepath):
    io=tool.IO_worker()
    text=io.read(filepath)
    confidentialRulesDict=encrypt_a_string(text)
    del text
    io.write_dict_to_jsonfile(confidentialRulesDict,"NCBI-confidentialRulesDict.json")
    return True


def test1():
    timer=tool.Timer()
    io=tool.IO_worker()
    cfg=blot.extractionLayer("BGL.txt",timer)
    io.write_Dic_to_Jsonfile(cfg,'CFG_BGL_normal')
    print(timer.get_elapsed_time('extractionLayer'))

def test2():
    timer = tool.Timer()
    io = tool.IO_worker()
    cfg=io.read_Dic_from_Jsonfile("./result/"+"CFG_BGL_normal")
    coded_cfg=blot.encodingLayer(cfg,timer)
    io.write_Dic_to_Jsonfile(coded_cfg,"codedCFG_BGL_normal")
    print(timer.get_elapsed_time("encodingLayer"))

def test3():
    timer = tool.Timer()
    io = tool.IO_worker()
    coded_cfg=io.read_Dic_from_Jsonfile("./result/"+"codedCFG_BGL_normal")
    encryted_cfg,rootKey=blot.substitutionLayer(coded_cfg,timer)
    io.write_Dic_to_Jsonfile(encryted_cfg,"encrytedCFG_BGL_normal")
    io.write_Dic_to_Jsonfile(rootKey,"rootKey_BGL_normal")
    print(timer.get_elapsed_time("substitutionLayer"))




# test3()

# sys.setrecursionlimit(10000000)
# encrypt_a_file('./NCBI.txt')
# encrypt_a_file('./test.txt')
# encrypt_a_file('./BC5CDR.txt')

# print(sequitur.run_sequitur_in_dic(text))


# io=tool.IO_worker()
# print("-----------------")
# text=io.read('./test2.txt')
# text=text.replace("/","")
# text=text.replace("\\","")
# text=text.replace('\"',"")
# text=text.replace('<',"")
# text=text.replace('>',"")
# print("********************************")
# print(sequitur.run_sequitur(text))


# path="./dataset1/awards_1990/awd_1990_00/a9000006.txt"
def encrypt_by_AES(path):
    io=tool.IO_worker()
    s=io.read(path)
    data=s.encode()
    aes_key = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_OCB)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    assert len(cipher.nonce) == 15
    with open("encrypted1.bin", "wb") as f:
        f.write(tag)
        f.write(cipher.nonce)
        f.write(ciphertext)
    return aes_key

def decrypt_by_AES(aes_key):
    with open("encrypted1.bin", "rb") as f:
        tag = f.read(16)
        nonce = f.read(15)
        ciphertext = f.read()
    cipher = AES.new(aes_key, AES.MODE_OCB, nonce=nonce)
    try:
        message = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        print("The message was modified!")
        sys.exit(1)
    print("Message:", message.decode())

# path="./dataset1/awards_1990/awd_1990_00/a9000006.txt"
def encrypt_and_decrypt_by_AES(path):
    #先加密，测试相关参数
    io=tool.IO_worker()
    s=io.read(path)
    data=s.encode()
    aes_key = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_OCB)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    assert len(cipher.nonce) == 15
    #再解密，测试相关参数
    nonce=cipher.nonce
    cipher2 = AES.new(aes_key, AES.MODE_OCB, nonce=nonce)
    try:
        message = cipher2.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        print("The message was modified!")
        sys.exit(1)
    print("Message:", message.decode())

def encrypt_and_decrypt_by_3DES(path):
    #生成密钥
    while True:
        try:
            key = DES3.adjust_key_parity(get_random_bytes(24))
            break
        except ValueError:
            pass
    #加密
    io=tool.IO_worker()
    s=io.read(path)
    plaintext=s.encode()
    cipher = DES3.new(key, DES3.MODE_CFB)
    iv=cipher.iv
    ciphertxt=cipher.encrypt(plaintext)
    #完成加密，接下来解密
    cipher2=DES3.new(key, DES3.MODE_CFB,iv=iv)
    try:
        message = cipher2.decrypt(ciphertxt)
    except ValueError:
        print("The message was modified!")
        sys.exit(1)
    print("Message:", message.decode())
