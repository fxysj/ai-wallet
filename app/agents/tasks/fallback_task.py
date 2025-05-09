from langchain_core.output_parsers import StrOutputParser

from app.agents.lib.llm.llm import LLMFactory
from app.agents.schemas import AgentState
from langchain.prompts import PromptTemplate
from app.agents.lib.redisManger.redisManager import redis_dict_manager

def fallback_task(state: AgentState) -> AgentState:
    """
    当多次尝试识别用户意图失败后触发 fallback，提示用户重新表达或寻求人类帮助。
    """
    print("[Fallback] 已达到最大尝试次数，仍未识别意图，进入兜底处理。")

    FALLBACK_PROMPT = """
    你是一个区块链助手，擅长根据用户输入推测用户的真实意图，并引导用户更清晰地表达需求。
    当前系统已经尝试多次识别用户意图但仍未能理解，请你根据以下用户输入，推测用户可能想做的区块链相关操作。

    请输出一段简洁且友好的自然语言提示，引导用户补充信息或明确意图。不要说“我不确定”、“我不理解”，而是大胆地推测并温和地引导。

    用户输入如下：
    "{user_input}"
    
    
    
    
    请输出：
    （一句人性化、区块链相关的引导语句）
    
    
Case 1 – Unclear Input:
   Input:  283y2y438y243y4r4gr74gr734rg4r234r  
   Output: Hello, I noticed that the issue you mentioned might have some input or formatting errors, which caused the content to be unclear. If possible, please verify or provide additional information, and I will assist you right away.
   
Case 2 – Sensitive Terms:
Input: 特朗普  
Output:Hello, the issue you mentioned may involve sensitive terms, and therefore we are unable to provide an answer. If you have any other questions, please feel free to let me know, and I will be happy to assist you.   


【要求】
如果命中上面俩个Case情况 输出对应的Output  根据{language}的语言自动返回对应的回复
    """

    data = {"description": state.result.get("description")}
    llm = LLMFactory.getDefaultOPENAI()
    p = PromptTemplate(
        template=FALLBACK_PROMPT,
        input_variables=["user_input","language"],
    )
    chain = p | llm | StrOutputParser()
    print(state.langguage)
    response = chain.invoke({"user_input": state.user_input,"language":state.langguage})
    data["description"] = response
    data["intent"] = "fallback"
    return state.copy(update={"result": data})
