sendsitive_keywords = [
    # 🚫 政治相关
    "特朗普", "川普", "习近平", "台独", "疆独", "港独", "国家主席", "共产党", "中共", "颠覆政权", "反动", "政府腐败",
    # 🚫 暴力恐怖
    "恐怖袭击", "爆炸物", "炸弹", "枪支", "暗杀", "武装暴动", "基地组织", "ISIS", "极端主义",
    # 🚫 色情低俗
    "黄片", "AV", "性交易", "裸聊", "约炮", "情色", "成人影片", "卖淫", "嫖娼", "打飞机",
    # 🚫 非法金融/诈骗
    "洗钱", "黑钱", "毒资", "黑钱交易", "电信诈骗", "庞氏骗局", "传销币", "虚假投资", "诈骗平台",
    # 🚫 宗教/种族敏感
    "伊斯兰圣战", "穆斯林暴动", "犹太人阴谋", "种族歧视", "纳粹", "白人至上", "黑鬼", "排华", "排外",
    # 🚫 违法活动
    "毒品交易", "贩毒", "黑社会", "开赌场", "走私", "地下钱庄", "网暴", "网络攻击", "DDoS", "黑客攻击",
    # 🚫 社会敏感
    "器官买卖", "人体试验", "活摘器官", "自杀直播", "跳楼", "割腕", "自焚",
    # 🚫 国际争议
    "台湾是国家", "中国不是一个国家", "承认西藏", "承认香港独立", "台海战争", "台湾总统",
    # 🚫 涉外机密
    "泄密", "国家机密", "军事基地", "卫星武器", "核弹部署"
]

#是否包含信息
def contains_sensitive_word(message: str, sensitive_list: list) -> bool:
    return any(word in message for word in sensitive_list)


def contains_sendtive_response(message: str) -> dict:
    isContainsSensitiveWord= contains_sensitive_word(message,sendsitive_keywords)
    if isContainsSensitiveWord:
        return {
            "data": {
                "description": "Hello, the issue you mentioned may involve sensitive terms, and therefore we are unable to provide an answer. If you have any other questions, please feel free to let me know, and I will be happy to assist you.",
                "intent": "unclear"
            }
        }
if __name__ == '__main__':
    res = contains_sendtive_response("特朗普")
    print(res)
