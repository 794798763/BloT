import time
import os
import json
import codecs


class ExperimentalRecord:

    def __init__(self):
        self.path=''
        self.size_before=0
        #path和sizebefore是需要提前获取的。其他数据是实验中获得并添加的
        self.size_after=0
        self.word_num=0
    #转dic方便转json，
    def to_dic(self):
        er_dic=dict()
        er_dic["path"]=self.path
        er_dic["size_before"]=self.size_before
        er_dic["size_after"]=self.size_after
        er_dic["word_num"]=self.word_num





#HDFS不适用，太大了。可以直接复制到word里看字数。公有方法，查看字符串的word—num
def count_words(string):
    temp_list=string.split()
    return len(temp_list)

#私有方法，删除数据集中的一些html数据
def search_dir_temp(path):
    files=os.listdir(path)
    for file in files:
        if os.path.isdir(path+'/'+file):
            search_dir_temp(path+'/'+file)
        else:
            print(path+'/'+file)
            if "html" in file:
                os.remove(path+'/'+file)

#获取文件夹下的所有file的路径,私有方法
def search_dir(path,relist):
    files=os.listdir(path)
    for file in files:
        if os.path.isdir(path+'/'+file):
            relist=search_dir(path+'/'+file,relist)
        else:
            relist.append(path+'/'+file)
    return relist

#返回的数据包括文本size，path，字数
def get_all_files_in_dir(dir_path):
    result_list=[]
    io=IO_worker()
    path_list=search_dir(dir_path,[])
    for file_path in path_list:
        er=ExperimentalRecord()
        er.path=file_path
        st=io.read(file_path)
        er.word_num=count_words(st)






#读写功能的类
class IO_worker():

    def read(self,path):
        with open(path,"r") as file:
            data=file.read()
            # print("read "+str(path)+" successfully")
            return data

    def write_file(self,filename,data):
        filepath = './result/' + filename
        with open(filepath,'w') as f:
            f.write(data)

    def write_Dic_to_Jsonfile(self,rules_dic,filename):
        filepath='./result/'+filename
        with open(filepath,'w') as f:
            json.dump(rules_dic,f)

    def read_Dic_from_Jsonfile(self,filepath):
        with open(filepath,'r') as f:
            data=f.read()
        return json.loads(data)

    def read_batch(self,path,batch_size_in_char):
        with open(path,"r") as file:
            data=file.read(batch_size_in_char)
            return data








#计时器功能
class Timer:
    #一个具有累加功能的计时器
    def __init__(self):
        self.timer_pool = dict()
    def start(self,id):
        starttime=time.time()
        #元组元素分别是 开始时间，结束时间，累计时间
        tup=self.timer_pool.pop(id,(0,0,0))
        endtime=0
        elapsedtime=tup[2]
        self.timer_pool[id]=(starttime,endtime,elapsedtime)
        return starttime
    def stop(self,id):
        endtime=time.time()
        tup = self.timer_pool.pop(id, (0, 0, 0))
        starttime=tup[0]
        elapsedtime=tup[2]
        self.timer_pool[id]=(starttime,endtime,endtime-starttime+elapsedtime)
        return endtime
    def get_elapsed_time(self,id):
        temp=self.timer_pool[id]
        return temp[2]

    def get_elapsed_time_in_ms(self,id):
        re=self.get_elapsed_time(id)
        return int(re*1000)

    def get_all_elapsed_time(self):
        re=dict()
        for key,value in self.timer_pool.items():
            re[key]=value[2]
        return re





# io=IO_worker()
# s=io.read("NCBI.txt")
# s=io.read("./dataset1/awards_1990/awd_1990_00/a9000006.txt")

# search_dir_temp("./dataset3")
# print(len(search_dir("./dataset3",[])))
# count_words(s)