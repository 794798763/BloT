import tool

STEP_SIZE = 100000

class ExtensionNode():
    def __init__(self,length,pointed_rule):
        self.type = "ExtensionNode"
        self.length=length
        self.pointed_rule=pointed_rule



class LeafNode():
    def __init__(self,length):
        self.type = "LeafNode"
        self.length = length

class RelayNode():
    def __init__(self,ofset,stake):
        self.type = "RelayNode"
        self.stake=stake
        self.ofset=ofset

#整个index由两部分构成，stepindex和ruleindex
#stepindex由RelayNode构成，索引固定步长的数据
#ruleindex的key是rule号，value是列表，列表放ExtensionNode或LeafNode
def print_stepindex(stepindex):
    re=[]
    for rnode in stepindex:
        r=dict()
        r["ofset"]=rnode.ofset
        r["stake"]=rnode.stake
        re.append(r)
    print(re)

def get_stepindex(stepindex):
    re=[]
    for rnode in stepindex:
        re.append((rnode.stake,rnode.ofset))
    return re

def print_ruleindex(ruleindex):
    re=dict()
    for rule_name, nodes in ruleindex.items():
        node_list = []
        for node in nodes:
            if node.type == "LeafNode":
                node_list.append({"type": "LeafNode", "length": node.length})
            else:
                node_list.append({
                    "type": "ExtensionNode",
                    "length": node.length,
                    "pointed_rule": node.pointed_rule
                })
        re[rule_name]=node_list
    print(re)

def get_ruleindex(ruleindex):
    re=dict()
    for rule_name, nodes in ruleindex.items():
        node_list = []
        for node in nodes:
            if node.type == "LeafNode":
                node_list.append(("L",node.length))
            else:
                node_list.append(("E",node.length,node.pointed_rule))
        re[rule_name]=node_list
    return re

def construct_ruleindex(cfg):
    length_of_rules=dict()
    ruleindex=dict()
    construct_a_ruleitem(cfg,"R0",length_of_rules,ruleindex)
    return ruleindex

#length_of_rules是字典，记录已经求得的rule长度防止重复遍历，ruleindex是字典记录最终的生成结果
def construct_a_ruleitem(cfg,rule_num,length_of_rules,ruleindex):
    leafNodeLength=0
    rule=cfg[rule_num]
    new_ruleindex_item=[]
    length_temp=0
    last_char_type="n"
    while len(rule)>0:
        char=rule[0]
        if "R" in char and len(char)>1:
            if last_char_type == "char":
                new_node=LeafNode(leafNodeLength)
                new_ruleindex_item.append(new_node)
                length_temp = length_temp + leafNodeLength
            if char not in length_of_rules.keys():
                construct_a_ruleitem(cfg, char, length_of_rules, ruleindex)
            new_node=ExtensionNode(length_of_rules[char],char)
            new_ruleindex_item.append(new_node)
            last_char_type="rule"
            length_temp = length_temp + length_of_rules[char]
        else:
            if last_char_type == "char":
                leafNodeLength=leafNodeLength+1
                last_char_type = "char"
            else:
                leafNodeLength=1
                last_char_type="char"
        if len(rule)==1:
            if last_char_type == "char":
                new_node = LeafNode(leafNodeLength)
                new_ruleindex_item.append(new_node)
                length_temp = length_temp + leafNodeLength
            break
        rule=rule[1:]
    ruleindex[rule_num]=new_ruleindex_item
    length_of_rules[rule_num]=length_temp
    print("完成rule： "+str(rule_num))
    return



def construct_ruleindex_old(cfg):
    ruleindex=dict()
    #暂时记录所有rule的长度
    length_of_rules=dict()
    leafNodeLength=0
    for snr in range(len(cfg)):
        ruleNum="R"+str(len(cfg)-1-snr)
        rule=cfg[ruleNum]
        new_ruleindex_item=[]
        length_temp=0
        last_char_type="n"
        while len(rule)>0:
            char=rule[0]
            if "R" in char and len(char)>1:
                if last_char_type == "char":
                    new_node=LeafNode(leafNodeLength)
                    new_ruleindex_item.append(new_node)
                    length_temp = length_temp + leafNodeLength
                new_node=ExtensionNode(length_of_rules[char],char)
                new_ruleindex_item.append(new_node)
                last_char_type="rule"
                length_temp = length_temp + length_of_rules[char]
            else:
                if last_char_type == "char":
                    leafNodeLength=leafNodeLength+1
                    last_char_type = "char"
                else:
                    leafNodeLength=1
                    last_char_type="char"
            if len(rule)==1:
                if last_char_type == "char":
                    new_node = LeafNode(leafNodeLength)
                    new_ruleindex_item.append(new_node)
                    length_temp = length_temp + leafNodeLength
                break
            rule=rule[1:]
        ruleindex[ruleNum]=new_ruleindex_item
        length_of_rules[ruleNum]=length_temp
    return ruleindex

def construct_stepindex(ruleindex):
    stepindex=[]
    pointer_in_stepindex=0
    count=0
    r0=ruleindex["R0"]
    for i,node in enumerate(r0):
        count=count+node.length
        if count >=pointer_in_stepindex*STEP_SIZE:
            if node.type=="LeafNode":
                new_node=RelayNode(pointer_in_stepindex*STEP_SIZE-(count-node.length),[("R0",i)])
                stepindex.append(new_node)
            else:
                s=list()
                s.append(("R0",i))
                new_node=find_underlying_node(ruleindex,node.pointed_rule,pointer_in_stepindex*STEP_SIZE-(count-node.length),s)
                stepindex.append(new_node)
            pointer_in_stepindex=pointer_in_stepindex+1
    return stepindex

def find_underlying_node(ruleindex,rule_name,ofset,stake):
    nodes=ruleindex[rule_name]
    count=0
    for i,node in enumerate(nodes):
        count=count+node.length
        if count>=ofset:
            if node.type=="LeafNode":
                stake.append((rule_name, i))
                new_node=RelayNode(ofset-(count-node.length),stake)
                return new_node
            else:
                stake.append((rule_name,i))
                new_node=find_underlying_node(ruleindex,node.pointed_rule,ofset-(count-node.length),stake)
                return new_node
    return None




