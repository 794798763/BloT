import blot
import tool
import VectorCommitment
import VC
from collections import deque
import json


unit_cost_of_a_proof=66
unit_cost_of_a_commitment=66
unit_cost_of_a_hash=16
unit_cost_of_a_node=2*unit_cost_of_a_hash+unit_cost_of_a_proof

per_height_cost_in_merkle_path = unit_cost_of_a_commitment+unit_cost_of_a_hash
per_height_cost_in_vector_commitment = unit_cost_of_a_commitment+unit_cost_of_a_proof

BatchSize = 1000000
stepsize=10000
DATASET = "BC5CDR"
timer=tool.Timer()

def measure_size_of_dict(my_dict):
    json_str = json.dumps(my_dict)
    json_bytes = json_str.encode('utf-8')
    json_length = len(json_bytes)
    return json_length

def safe_pop(stake):
    try:
        return stake.pop()
    except IndexError:
        return None

def node_id_to_rule_name(node_id):
    return "R"+str(node_id-1)


def rule_name_to_node_id(rule_name):
    return int(rule_name[1:])+1


#获得遍历到目标rule时，该目标到R0的栈
def get_stake_to_R0(ofset):
    io = tool.IO_worker()
    cfg = io.read_Dic_from_Jsonfile("./result/" + DATASET + "-B0-cfg.json")
    print("cfg读入完成")
    ifsi = io.read_Dic_from_Jsonfile("./result/" + DATASET + "-B0-IFSI.json")["result"]
    print("ifsi读入完成")

    ofset_in_batch=ofset%BatchSize
    iter=int(ofset_in_batch/stepsize)
    count=iter*stepsize
    stake=ifsi[iter]
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
            if len(char) ==1:
                count=count+1
                if count==ofset_in_batch:
                    stake.append((rule_name, char_pointer + b))
                    print(str(ofset)+"处理完成，获得栈："+str(stake))
                    return stake
            else:
                stake.append((rule_name,char_pointer+b))
                stake.append((char,-1))
                break
        # print("经过一条rule：" + str(rule_name))

    return None

def topological_sort(cfg):
    #记录都有哪些rule指向了这个rule
    pre_rules=dict()
    pre_rules["R0"]=set()
    # 计算每个节点的出度
    out_degree = dict()
    for rule_name in cfg.keys():
        ts=set()
        for neighbor in cfg[rule_name]:
            if len(neighbor)>1:
                ts.add(neighbor)
                if neighbor in pre_rules.keys():
                    temp_set=pre_rules[neighbor]
                    temp_set.add(rule_name)
                    pre_rules[neighbor]=temp_set
                else:
                    temp_set=set()
                    temp_set.add(rule_name)
                    pre_rules[neighbor] = temp_set
        out_degree[rule_name]=len(ts)
    # 初始化队列，将所有入出度为0的节点加入队列
    queue = deque([rule_name for rule_name in out_degree.keys() if out_degree[rule_name] == 0])
    result = []

    while queue:
        # 从队列中取出一个节点
        current = queue.popleft()
        result.append(current)
        # 处理当前节点的所有邻居
        for pre in pre_rules[current]:
            out_degree[pre] -= 1
            # 如果邻居的入度变为0，将其加入队列
            if out_degree[pre] == 0:
                queue.append(pre)

    # 检查是否所有节点都被排序，如果不是，则说明图中存在环
    print("拓扑排序完成")
    print(result)
    if len(result) != len(cfg):
        print("CFG contains a cycle")
        return None

    return result

def get_coordinate_to_ofset(ofset):
    io = tool.IO_worker()
    cfg = io.read_Dic_from_Jsonfile("./result/" + DATASET + "-B0-cfg.json")
    print("cfg读入完成")
    ifsi = io.read_Dic_from_Jsonfile("./result/" + DATASET + "-B0-IFSI.json")["result"]
    print("ifsi读入完成")

    ofset_in_batch=ofset%BatchSize
    iter=int(ofset_in_batch/stepsize)
    count=iter*stepsize
    stake=ifsi[iter]
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
            if len(char) ==1:
                count=count+1
                if count==ofset_in_batch:
                    stake.append((rule_name, char_pointer + b))
                    print(str(ofset)+"处理完成，获得栈："+str(stake))
                    return rule_name,char_pointer+b
            else:
                stake.append((rule_name,char_pointer+b))
                stake.append((char,-1))
                break
        # print("经过一条rule：" + str(rule_name))

    return None

def get_merkle_proof_cost_of_node_to_validited(node_id,validated_style):
    temp_cost=0
    while True:
        if node_id in validated_style.keys():
            return temp_cost
        node_id=int(node_id/2)
        temp_cost=temp_cost+per_height_cost_in_merkle_path


def construct_ads_baseline():
    io = tool.IO_worker()
    cfg = io.read_Dic_from_Jsonfile("./result/" + DATASET + "-B0-cfg.json")
    print("cfg读入完成")
    #commitments、Hs、master_secrets是对每一条rule使用向量承诺算法生成的参数，字典类型，key是rulename，value分别是承诺、H、和master_secret
    Hs=dict()
    master_secrets=dict()
    commitments=dict()
    p_count=0

    #ads_nodes是ads树上的所有节点，字典类型
    ads_nodes=dict()

    #根据拓扑排序的顺序建立各个rule的向量承诺
    timer.start("sort")
    order=topological_sort(cfg)
    timer.stop("sort")
    vectors=dict()
    for rule_name in order:
        vector=[]
        for i in cfg[rule_name]:
            p_count+=1
            if len(i)>1:
                vector.append(hash(commitments[i]))
            else:
                vector.append(hash(i))
        vectors[rule_name]=vector
        vc = VC.VectorCommitment()
        H, master_secret = vc.setup(len(vector))
        H=VC.points_to_compressed_string(H)
        Hs[rule_name] = H
        master_secrets[rule_name] = master_secret
        timer.start("commit")
        commitment = vc.commit(VC.compressed_string_to_points(H), vector, master_secret)
        timer.stop("commit")
        commitment=VC.point_to_compressed_string(commitment)
        commitments[rule_name] = commitment
        print("已为节点生成向量承诺   ",rule_name)

    #开始建立树
    #先计算树高
    h=1
    while pow(2,h-1)<len(cfg):
        h+=1
    print("开始建立树")
    print("pcount是 "+str(p_count))
    #第h层上的节点都是叶子节点，先计算这些节点的hash
    node_id=pow(2,h-1)-1
    for i in range(len(cfg)):
        rule_name=node_id_to_rule_name(i+1)
        ads_nodes[node_id+i]=hash(commitments[rule_name])
    #开始从下往上构建h-1层到1层
    node_id=pow(2,h-1)-1
    while node_id>0:
        h1 = 0
        h2 = 0
        if node_id*2 in ads_nodes.keys():
            h1=ads_nodes[node_id*2]
        if node_id*2+1 in ads_nodes.keys():
            h2=ads_nodes[node_id*2+1]
        temp_hash=hash(str(h1)+str(h2))
        ads_nodes[node_id]=temp_hash
        node_id=node_id-1
    tree=dict()
    tree["ads_nodes"]=ads_nodes
    tree["commitments"]=commitments
    io.write_Dic_to_Jsonfile(tree,DATASET+"-B0-ads-baseline.json")
    records=dict()
    records["root"]=str(ads_nodes[1])
    records["Hs"]=Hs
    records["vectors"]=vectors
    records["master_secrets"]=master_secrets
    io.write_Dic_to_Jsonfile(records,DATASET+"-B0-ads-params-baseline.json")
    return Hs,master_secrets,ads_nodes,str(ads_nodes[1])

def exp_contruct_VO_1_time_baseline(ofset):
    #载入参数
    io=tool.IO_worker()
    params = io.read_Dic_from_Jsonfile("./result/" + DATASET + "-B0-ads-params-baseline.json")
    tempdict = io.read_Dic_from_Jsonfile("./result/" + DATASET + "-B0-ads-baseline.json")
    ads_nodes=tempdict["ads_nodes"]
    commitments=tempdict["commitments"]
    Hs=params["Hs"]
    vectors=params["vectors"]
    root=params["root"]
    master_secrets=params["master_secrets"]
    #构造vo
    # vo_commitments：字典，记录rule的commitment；
    # vo_proof：两层的字典，第一层是rule_name，第二层是SNC；
    # vo_hash_of_nodes 字典，记录每个节点对应的hash
    vo_commitments=dict()
    vo_proof=dict()
    vo_hash_of_nodes=dict()
    #计算除叶子节点外的树高
    # 先计算树高,
    #计算非叶子节点数
    h = 1
    while pow(2, h - 1) < len(master_secrets):
        h += 1
    base_nodes_num=pow(2, h-1)-1
    #计算坐标
    SNR,SNC=get_coordinate_to_ofset(ofset)
    nodeid=rule_name_to_node_id(SNR)
    #制造承诺
    vo_commitments[SNR]=commitments[SNR]
    #制造证明
    vc = VC.VectorCommitment()
    proof = vc.proof(VC.compressed_string_to_points(Hs[SNR]), vectors[SNR], SNC, master_secrets[SNR])
    if SNR in vo_proof.keys():
        vo_proof[SNR][SNC]=VC.point_to_compressed_string(proof)
    else:
        temp=dict()
        temp[SNC]=VC.point_to_compressed_string(proof)
        vo_proof[SNR]=temp
    #添加mpt路径
    i=base_nodes_num+nodeid
    while i>0:
        vo_hash_of_nodes[i]=ads_nodes[str(i)]
        i=int(i/2)
    #构造最终的vo
    record=dict()
    record["commitments"]=vo_commitments
    record["proof"]=vo_proof
    record["hash_of_nodes"]=vo_hash_of_nodes
    record["root"]=root
    return record





def sel_disclose(start,end):
    #validated_style的key是node_id,value是”VC“或”MPT“。
    #vc_pieces_in_vo是列表，列表的每个元素是个元组，第一位是rulename，第二位是在rulename中的位置

    validated_style = dict()
    validated_style[1]="MPT"
    vc_pieces_in_vo = []
    i=start
    while i<=end:
        print("正在处理ofset="+str(i))
        construct_VO_by_ofset(i,validated_style,vc_pieces_in_vo)
        i+=1
        print(validated_style)
        print(vc_pieces_in_vo)
    print(validated_style)
    print(vc_pieces_in_vo)


def construct_VO_by_ofset(ofset,validated_style,vc_pieces_in_vo):
    #先获得向量承诺的stake，stake中有多少节点就有多少种接入已验证路径的可能
    node_stake=get_stake_to_R0(ofset)
    if len(node_stake)<1:
        return
    cheapest_cost=10000000000
    cheapest_path=[]
    cheapest_start=None
    base_vc_cost=2*unit_cost_of_a_hash
    while len(node_stake)>0:
        position=safe_pop(node_stake)
        cheapest_path.append(position)
        SNR=position[0]
        node_id_of_SNR=rule_name_to_node_id(SNR)
        if SNR=="R0":
            print("跳过R0")
            continue
        temp_cost=base_vc_cost+get_merkle_proof_cost_of_node_to_validited(node_id_of_SNR,validated_style)
        if temp_cost<cheapest_cost:
            cheapest_start=position
            cheapest_cost=temp_cost
        base_vc_cost=base_vc_cost+per_height_cost_in_vector_commitment
    print("找到代价最低路径  "+str(cheapest_start))
    while True:
        i=safe_pop(cheapest_path)
        if i == cheapest_start:
            cheapest_path.append(i)
            break
    print("代价最低的路径是  "+str(cheapest_path) )
    if len(cheapest_path)>1:
        vc_pieces_in_vo.append(cheapest_path)
    for i in cheapest_path:
        r_nodeid = rule_name_to_node_id(i[0])
        if r_nodeid in validated_style.keys():
            continue
        validated_style[r_nodeid]="VC"
    i=rule_name_to_node_id(cheapest_start[0])
    validated_style[i]="MPT"
    while i>=1:
        if i in validated_style.keys():
            i=int(i/2)
            continue
        validated_style[i] = "MPT"
        i = int(i / 2)
    return validated_style,vc_pieces_in_vo



def construct_ADS():
    io = tool.IO_worker()
    cfg = io.read_Dic_from_Jsonfile("./result/" + DATASET + "-B0-cfg.json")
    print("cfg读入完成")
    #commitments、Hs、master_secrets是对每一条rule使用向量承诺算法生成的参数，字典类型，key是rulename，value分别是承诺、H、和master_secret
    Hs=dict()
    master_secrets=dict()
    commitments=dict()
    p_count=0

    #ads_nodes是ads树上的所有节点，字典类型，key是nodeid，value是三元组，第一位是左孩子，第二位是右孩子，第三位是commitment
    ads_nodes=dict()
    #key是nodeid，value是node的hash
    hashs_of_nodes=dict()

    #根据拓扑排序的顺序建立各个rule的向量承诺
    timer.start("sort")
    order=topological_sort(cfg)
    timer.stop("sort")
    vectors=dict()

    for rule_name in order:
        vector=[]
        for i in cfg[rule_name]:
            p_count+=1
            if len(i)>1:
                vector.append(hash(commitments[i]))
            else:
                vector.append(hash(i))

        vectors[rule_name]=vector
        vc = VC.VectorCommitment()
        H, master_secret = vc.setup(len(vector))
        H=VC.points_to_compressed_string(H)
        Hs[rule_name] = H
        master_secrets[rule_name] = master_secret
        timer.start("commit")
        commitment = vc.commit(VC.compressed_string_to_points(H), vector, master_secret)
        timer.stop("commit")
        commitment=VC.point_to_compressed_string(commitment)
        commitments[rule_name] = commitment
        print("已为节点生成向量承诺   ",rule_name)
    #开始建立树
    print("开始建立树")
    print("pcount是 "+str(p_count))
    node_id=len(cfg.keys())
    timer.start("tree")
    while node_id>0:
        rule_name=node_id_to_rule_name(node_id)
        h1=0
        h2=0
        if 2*node_id<=(len(cfg.keys())):
            h1=hashs_of_nodes[2*node_id]
        if 2*node_id+1<=(len(cfg.keys())):
            h2=hashs_of_nodes[2*node_id+1]
        temp_hash=hash(str(h1)+str(h2)+commitments[rule_name])
        hashs_of_nodes[node_id]=temp_hash
        ads_nodes[node_id]=(str(h1),str(h2),commitments[rule_name])
        node_id-=1
    timer.stop("tree")
    io.write_Dic_to_Jsonfile(ads_nodes,DATASET+"-B0-ads.json")
    records=dict()
    records["root"]=str(hashs_of_nodes[1])
    records["vectors"]=vectors
    records["Hs"]=Hs
    records["master_secrets"]=master_secrets
    io.write_Dic_to_Jsonfile(records,DATASET+"-B0-ads-params.json")
    return Hs,master_secrets,ads_nodes,str(hashs_of_nodes[1])








def exp_contruct_VO_10000_times():

    for i in range(10000):
        return True


def exp_contruct_VO_1_time(ofset):
    #获得路径
    validated_style = dict()
    validated_style[1]="MPT"
    vc_pieces_in_vo = []
    construct_VO_by_ofset(ofset,validated_style,vc_pieces_in_vo)
    print(validated_style)
    print(vc_pieces_in_vo)
    #载入参数
    io=tool.IO_worker()
    params = io.read_Dic_from_Jsonfile("./result/" + DATASET + "-B0-ads-params.json")
    ads_nodes = io.read_Dic_from_Jsonfile("./result/" + DATASET + "-B0-ads.json")
    Hs=params["Hs"]
    root=params["root"]
    master_secrets=params["master_secrets"]
    vectors=params["vectors"]
    #构造vo
    #vo有三部分组成，
    # vo_commitments：字典，记录每个rule的commitment；
    #vo_vc_path:list，里面多个子列表，每个子列表记录了一条向量验证的路径
    # vo_proof：两层的字典，第一层是rule_name，第二层是SNC；
    # vo_h1:字典，key是rulename，找到该规则对应的node的h1；
    # vo_h2：字典，key是rulename，找到该规则对应的node的h2
    vo_commitments=dict()
    vo_vc_paths=[]
    vo_proof=dict()
    vo_h1=dict()
    vo_h2=dict()
    #分三步走 1.获取目标偏移的坐标，找到对应的哈希，为哈希生成向量承诺
    SNR,SNC=get_coordinate_to_ofset(ofset)
    nodeid=rule_name_to_node_id(SNR)
    vc=VC.VectorCommitment()
    proof=vc.proof(VC.compressed_string_to_points(Hs[SNR]),vectors[SNR],SNC,master_secrets[SNR])
    vo_commitments[SNR]=ads_nodes[str(nodeid)][2]
    if SNR in vo_proof.keys():
        vo_proof[SNR][SNC]=VC.point_to_compressed_string(proof)
    else:
        temp=dict()
        temp[SNC]=VC.point_to_compressed_string(proof)
        vo_proof[SNR]=temp
    #2.根据vc_pieces_in_vo中的片段，为每一个片段上的节点生成承诺
    for piece in vc_pieces_in_vo:
        if len(piece)>1:
            vo_vc_paths.append(piece)
            pre=piece.pop(0)
            p=piece.pop(0)
            rule_name_pre=pre[0]
            nodeid_pre=rule_name_to_node_id(rule_name_pre)
            vo_commitments[rule_name_pre]=ads_nodes[str(nodeid_pre)][2]
            SNR=p[0]
            SNC=p[1]
            proof = vc.proof(VC.compressed_string_to_points(Hs[SNR]), vectors[SNR], SNC, master_secrets[SNR])
            if SNR in vo_proof.keys():
                vo_proof[SNR][SNC] = VC.point_to_compressed_string(proof)
            else:
                temp = dict()
                temp[SNC] = VC.point_to_compressed_string(proof)
                vo_proof[SNR] = temp
            while len(piece)>0:
                pre=p
                p=piece.pop(0)
                rule_name_pre = pre[0]
                nodeid_pre = rule_name_to_node_id(rule_name_pre)
                vo_commitments[rule_name_pre] = ads_nodes[str(nodeid_pre)][2]
                SNR = p[0]
                SNC = p[1]
                proof = vc.proof(VC.compressed_string_to_points(Hs[SNR]), vectors[SNR], SNC, master_secrets[SNR])
                if SNR in vo_proof.keys():
                    vo_proof[SNR][SNC] = VC.point_to_compressed_string(proof)
                else:
                    temp = dict()
                    temp[SNC] = VC.point_to_compressed_string(proof)
                    vo_proof[SNR] = temp
    #3.validated_style中所有的MPT类型，h1 h2 vc放进去
    for nodeid in validated_style.keys():
        rule_name=node_id_to_rule_name(nodeid)
        if validated_style[nodeid]=="VC":
            continue
        #如果左孩子也需要通过MPT进行验证，那么不需要提供h1
        if 2*nodeid in validated_style.keys() and validated_style[2*nodeid]=="MPT":
            pass
        else:
            vo_h1[rule_name] = ads_nodes[str(nodeid)][0]
        #如果右孩子也需要通过MPT进行验证，那么不需要提供h2
        if 2*nodeid+1 in validated_style.keys() and validated_style[2*nodeid+1]=="MPT":
            pass
        else:
            vo_h2[rule_name] = ads_nodes[str(nodeid)][1]
        vo_commitments[rule_name]=ads_nodes[str(nodeid)][2]
    re=dict()
    re["commitments"]=vo_commitments
    re["vc_paths"]=vo_vc_paths
    re["proof"]=vo_proof
    re["h1"]=vo_h1
    re["h2"]=vo_h2
    re["root"]=root
    return re
    #construct_VO_by_ofset 函数有问题，成本比较前忘记叠加vc成本了(已完成)
    #在construct函数里应该把vector全部保存下来（已完成）
    # #现在cfg的引用是数字大的在上，数字小的在下，这导致越经过vc nodeid越大，hash成本越高。要写个反转函数生成cfg时翻转过来(已完成)



#commitments、Hs、master_secrets是对每一条rule使用向量承诺算法生成的参数，字典类型，key是rulename，value分别是承诺、H、和master_secret
# sel_disclose(10010,10030)
# print(get_stake_to_R0(10
# exp_contruct_VO_1_time(10099)
# construct_ADS()
# print(get_coordinate_to_ofset(10011))
record=exp_contruct_VO_1_time(10010)

# construct_ads_baseline()
# record=exp_contruct_VO_1_time_baseline(10010)
s=measure_size_of_dict(record)
print(s)
# construct_ads_baseline()
