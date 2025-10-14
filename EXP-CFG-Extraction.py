import os
import sys
import tool
import blot
import sequitur2
MAX_FILE_NUM = 5000-1
BATCH_SIZE = 1000

def exp_CFG_extract_time():
    """
    读取指定目录下的所有 .txt 文件,开展结构提取
    """
    #控制循环
    count=0
    #统计结果
    raw_data_size=0
    rule_num_accumulated=0
    char_num_accumulated = 0
    timer=tool.Timer()
    # 遍历目录下的所有文件
    for dirpath, dirnames, filenames in os.walk("dataset1"):
        for filename in filenames:
            #打开文件
            io=tool.IO_worker()
            data=io.read(os.path.join(dirpath,filename))
            raw_data_size=raw_data_size+sys.getsizeof(data)/1024 #单位kb
            count = count + 1

            #处理每个文件夹里的数据
            # print(data)
            seq = sequitur2.Sequitur2()
            newString = data.replace('/', "")
            timer.start((int(count/BATCH_SIZE)+1)*BATCH_SIZE)
            seq.run_new_string(newString)
            #在固定采样间隔记录实验结果
            timer.stop((int(count/BATCH_SIZE)+1)*BATCH_SIZE)
            seq.wash_rules_by_usage()
            CFG=seq.get_rules_in_dict()
            for rule,chars in CFG.items():
                rule_num_accumulated=rule_num_accumulated+1
                char_num_accumulated=char_num_accumulated+2+len(chars)

            # print("new file " + str(count) + " success")

            if int(count/BATCH_SIZE)>int((count-1)/BATCH_SIZE):
                print("固定间隔累计文件原始大小："+str(raw_data_size))
                print("固定间隔累计rule数量："+str(rule_num_accumulated))
                print("固定间隔累计密文大小："+str((char_num_accumulated*28)/1024))
            #遍历的数量足够多，跳出循环
            if (count>=MAX_FILE_NUM):
                break
        if (count >= MAX_FILE_NUM):
            print(timer.get_all_elapsed_time())
            print("固定间隔累计文件原始大小：" + str(raw_data_size))
            print("固定间隔累计rule数量："+str(rule_num_accumulated))
            print("固定间隔累计char数量："+str((char_num_accumulated*28)/1024))
            break

def exp_ruleNum_and_charNum():
    testBatch=5000
    # 控制循环
    count=0
    #统计结果
    rule_num_accumulated=0
    char_num_accumulated = 0
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
            #在固定采样间隔记录实验结果
            if count>testBatch:
                break
        if count>testBatch:
            break
    seq.wash_rules_by_usage()
    CFG=seq.get_rules_in_dict()
    for rule,chars in CFG.items():
        rule_num_accumulated=rule_num_accumulated+1
        char_num_accumulated=char_num_accumulated+1+len(chars)
    print(str(testBatch)+" 个文件产生rule数量：" + str(rule_num_accumulated))
    print(str(testBatch)+" 个文件产生char：" + str(char_num_accumulated))
    print(str(testBatch)+" 个文件产生密文大小：" + str((char_num_accumulated * 3) / 1024))#每个char占3个字节，换算成千字节KB

def exp_encrypt_time():
    testBatch=3000
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
            #在固定采样间隔记录实验结果
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
    print(str(testBatch)+" 个文件编码耗时：" + str(timer.get_elapsed_time("encodingLayer")))
    print(str(testBatch)+" 个文件代换耗时：" + str(timer.get_elapsed_time("substitutionLayer")))
    print(str(testBatch)+" 个文件加密总耗时：" + str(timer.get_elapsed_time(testBatch)))
    # print(str(testBatch)+" 个文件产生密文大小：" + str((char_num_accumulated * 3) / 1024))#每个char占3个字节，换算成千字节KB
exp_encrypt_time()