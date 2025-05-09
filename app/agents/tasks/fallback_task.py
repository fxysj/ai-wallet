from langchain.agents import initialize_agent, AgentType
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool
from langchain_tavily import TavilySearch
from app.agents.lib.llm.llm import LLMFactory
from app.agents.schemas import AgentState
from langchain.prompts import PromptTemplate

SENSITIVE_WORDS = [
    # 政治相关
    "习近平", "毛泽东", "周恩来", "邓小平", "江泽民", "胡锦涛", "李克强", "中共", "共产党", "政府", "政变", "政权", "暴政",
    "民主自由", "法轮功", "台独", "港独", "疆独", "西藏独立", "六四", "8964", "天安门", "退党", "反共", "异议人士",

    # 涉外敏感人物或话题
    "特朗普", "拜登", "普京", "习近平和特朗普", "乌克兰战争", "以巴冲突", "恐怖分子", "基地组织",

    # 暴力恐怖类
    "恐怖主义", "爆炸", "炸弹", "枪支", "暗杀", "斩首", "自杀袭击", "暴力革命", "起义", "暴动", "政变",

    # 犯罪、违法
    "毒品", "走私", "洗钱", "贩毒", "人口贩卖", "地下钱庄", "非法集资", "赌博", "诈骗", "网络攻击", "木马病毒", "勒索软件",

    # 涉黄涉暴
    "成人电影", "黄片", "嫖娼", "卖淫", "裸聊", "强奸", "性侵犯", "恋童", "兽交", "AV", "色情", "裸照",

    # 网络用语（隐晦替代）
    "包子", "膜蛤", "蛤蛤", "8964", "草泥马", "习大大", "政zhi", "Zhengfu", "NMSL", "支那", "你妈死了",

    # 区块链风险词（金融监管类）
    "跑路", "非法集资", "传销币", "资金盘", "庞氏骗局", "圈钱", "ICO", "STO非法", "代投", "韭菜",

    # 其他系统关键字
    "root权限", "黑客攻击", "远程控制", "后门", "监听", "抓包", "FBI", "NSA", "中情局"
]

tools = [Tool.from_function(name="TavilySearch",func=TavilySearch(max_retries=2),description="搜索引擎")]

def searchTools():
    explanations = []
    agent = initialize_agent(tools=tools,llm=LLMFactory.getDefaultOPENAI(),agent=AgentType.OPENAI_FUNCTIONS)
    for word in SENSITIVE_WORDS:
        prompt = f"请根据“{word}”一词在敏感词过滤系统中的含义 进行衍生出对应的类型的敏感词。衍生出10-20个敏感词"
        explanation = agent.invoke(prompt)
        explanations.append(f"{word}：{explanation}")

    return explanations

#对上面的敏感词进行重新生成
#参考定义的类型进行扩展
def extend_SENSITIVE_WORDS(words=SENSITIVE_WORDS):
    pro = PromptTemplate(
        template="""根据提供的敏感词汇 根据类型 进行扩展和补充 返回字符串格式 每个词汇 ,隔开
        敏感词汇: {words}
        """,
        input_variables=["words"]
    )
    chain = pro | LLMFactory.getDefaultOPENAI()|StrOutputParser()
    return chain.invoke({"words": words})



def fallback_task(state: AgentState) -> AgentState:
    """
    当多次尝试识别用户意图失败后触发 fallback，提示用户重新表达或寻求人类帮助。
    """
    print("[Fallback] 已达到最大尝试次数，仍未识别意图，进入兜底处理。")

    FALLBACK_PROMPT = """
    你是一个区块链助手，擅长根据用户输入推测用户的真实意图，并引导用户更清晰地表达需求。
    当前系统已经尝试多次识别用户意图但仍未能理解，请你根据以下用户输入和敏感词库，推测用户可能想做的区块链相关操作。
     
    【敏感词库】：
    {sens_words}


    请输出一段简洁且友好的自然语言提示，引导用户补充信息或明确意图。不要说“我不确定”、“我不理解”，而是大胆地推测并温和地引导。

    用户输入如下：
    "{user_input}"
    
    请严格按照以下规则输出（不要额外说明）：

【规则】
1. 如果用户输入命中敏感词库中的任意词，则固定输出：
   Hello, the issue you mentioned may involve sensitive terms, and therefore we are unable to provide an answer. If you have any other questions, please feel free to let me know, and I will be happy to assist you.

2. 如果用户输入是乱码或无法理解（如 Case 1），则输出：
   Hello, I noticed that the issue you mentioned might have some input or formatting errors, which caused the content to be unclear. If possible, please verify or provide additional information, and I will assist you right away.

3. 如果以上两种情况都不满足，请推测用户可能的区块链意图，并输出一句简洁、自然、人性化的引导语。
    
4. 返回语言应使用 {language} 所指定的语言 

    
    
Case 1 – Unclear Input:
   Input:  283y2y438y243y4r4gr74gr734rg4r234r  
   Output: Hello, I noticed that the issue you mentioned might have some input or formatting errors, which caused the content to be unclear. If possible, please verify or provide additional information, and I will assist you right away.
   
Case 2 – Sensitive Terms:
Input: 特朗普  
Output:Hello, the issue you mentioned may involve sensitive terms, and therefore we are unable to provide an answer. If you have any other questions, please feel free to let me know, and I will be happy to assist you.   

    """

    data = {}
    llm = LLMFactory.getDefaultOPENAI()
    p = PromptTemplate(
        template=FALLBACK_PROMPT,
        input_variables=["user_input","language","sens_words"],
    )
    chain = p | llm | StrOutputParser()
    response = chain.invoke({"user_input": state.user_input,"language":state.langguage,"sens_words":SENSITIVE_WORDS})
    data["description"] = response
    data["intent"] = "fallback"
    return state.copy(update={"result": data})
