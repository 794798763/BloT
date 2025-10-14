import tool

from collections import deque
import sys


class ExtensionNode:
    __slots__ = ('type', 'length', 'pointed_rule')  # 减少内存占用

    def __init__(self, length, pointed_rule):
        self.type = "ExtensionNode"
        self.length = length
        self.pointed_rule = pointed_rule


class LeafNode:
    __slots__ = ('type', 'length')  # 减少内存占用

    def __init__(self, length):
        self.type = "LeafNode"
        self.length = length


def construct_ruleindex(cfg):
    length_of_rules = {}
    ruleindex = {}
    dependency_map = {}  # 记录规则依赖关系
    ready_queue = deque()  # 处理队列（BFS代替递归）

    # 初始化依赖关系和叶子规则
    for rule_num, tokens in cfg.items():
        has_dependency = False
        for token in tokens:
            if token.startswith("R") and len(token) > 1:
                has_dependency = True
                # 记录依赖关系
                if token not in dependency_map:
                    dependency_map[token] = set()
                dependency_map[token].add(rule_num)

        # 没有依赖的规则直接处理
        if not has_dependency:
            ready_queue.append(rule_num)

    # 处理队列中的规则（BFS）
    while ready_queue:
        rule_num = ready_queue.popleft()

        # 如果已经处理过则跳过（避免重复）
        if rule_num in ruleindex:
            continue

        # 处理当前规则
        tokens = cfg[rule_num]
        new_ruleindex_item = []
        total_length = 0

        for token in tokens:
            if token.startswith("R") and len(token) > 1 and token in length_of_rules:
                # 处理规则引用
                new_node = ExtensionNode(length_of_rules[token], token)
                new_ruleindex_item.append(new_node)
                total_length += length_of_rules[token]
            else:
                # 处理普通token
                token_length = len(token) if isinstance(token, str) else 1
                new_node = LeafNode(token_length)
                new_ruleindex_item.append(new_node)
                total_length += token_length

        # 存储结果
        ruleindex[rule_num] = new_ruleindex_item
        length_of_rules[rule_num] = total_length

        # 检查依赖此规则的规则是否准备好
        if rule_num in dependency_map:
            for dependent_rule in dependency_map[rule_num]:
                # 检查依赖是否都已满足
                dependencies = [t for t in cfg[dependent_rule]
                                if t.startswith("R") and len(t) > 1]
                if all(dep in ruleindex for dep in dependencies):
                    ready_queue.append(dependent_rule)

    # 确保所有规则都已处理
    for rule_num in cfg:
        if rule_num not in ruleindex:
            ready_queue.append(rule_num)
            while ready_queue:
                # 简单处理未完成的规则
                rule_num = ready_queue.popleft()
                if rule_num not in ruleindex:
                    construct_fallback(cfg, rule_num, length_of_rules, ruleindex)

    return ruleindex


def construct_fallback(cfg, rule_num, length_of_rules, ruleindex):
    """后备处理方法（用于未解析的规则）"""
    tokens = cfg[rule_num]
    new_ruleindex_item = []
    total_length = 0

    for token in tokens:
        if token.startswith("R") and len(token) > 1:
            # 如果引用的规则还未处理，使用默认值
            ref_length = length_of_rules.get(token, 0)
            if token not in ruleindex:
                # 尝试直接处理引用的规则
                construct_fallback(cfg, token, length_of_rules, ruleindex)
                ref_length = length_of_rules.get(token, 0)

            new_node = ExtensionNode(ref_length, token)
            new_ruleindex_item.append(new_node)
            total_length += ref_length
        else:
            token_length = len(token) if isinstance(token, str) else 1
            new_node = LeafNode(token_length)
            new_ruleindex_item.append(new_node)
            total_length += token_length

    ruleindex[rule_num] = new_ruleindex_item
    length_of_rules[rule_num] = total_length

def construct_index(cfg_path):
    io=tool.IO_worker()
    cfg=io.read_Dic_from_Jsonfile(cfg_path)
    timer=tool.Timer()
    timer.start("ruleindex")
    ri=construct_ruleindex(cfg)
    timer.stop("ruleindex")
    # timer.start("stepindex")
    # si=construct_stepindex(ri)
    # timer.stop("stepindex")
    # io.write_Dic_to_Jsonfile(get_ruleindex(ri),"BGL-ruleindex.json")
    # io.write_Dic_to_Jsonfile(get_stepindex(si),"BGL-stepindex.json")
    print("ruleindex的构造耗时是：  "+str(timer.get_elapsed_time("ruleindex")))
    # print("stepindex的构造耗时是：  "+str(timer.get_elapsed_time("stepindex")))
construct_index("./result/NCBI-cfg.json")
