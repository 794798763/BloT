import tool

def safe_pop(l):
    try:
        return l.pop()
    except IndexError:
        return None

def make_IFSI(cfg):
    STEPSIZE=10000
    STEP=0
    stepindex=[]
    count=-1
    stake=[("R0",-1)]
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
                if count==STEP*STEPSIZE:
                    stake.append((rule_name,char_pointer+b))
                    stepindex.append(stake.copy())
                    stake.pop()
                    print("处理完成字符数："+str(STEP*STEPSIZE))
                    STEP = STEP + 1
            else:
                stake.append((rule_name,char_pointer+b))
                stake.append((char,-1))
                break
    re=dict()
    re["result"]=stepindex
    return re

