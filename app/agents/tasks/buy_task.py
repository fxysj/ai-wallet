# 处理购买任务
import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.form.form import TaskState
from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.buy_prompt_en import BUYTASK_TEMPLATE
from app.agents.schemas import AgentState
from app.utuls.FieldCheckerUtil import FieldChecker

async def buy_task(state: AgentState) -> AgentState:
    print("buy_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))    
    print("DEBUG - attached_data 内容:", state.attached_data)
    prompt = PromptTemplate(
        template=BUYTASK_TEMPLATE,
        input_variables=["current_data", "history", "input", "langguage", "chain_data"],
    )
    llm = LLMFactory.getDefaultOPENAI()
    # 使用新版输出解析器
    # 如果 返回的结果确定下来 chain = prompt | llm | JsonOutputParser(pydantic_model=FullTransactionResponse)
    chain = prompt | llm | JsonOutputParser()
    # 调用链处理用户最新输入
        # Prepare prompt variables and add chain_data
    prompt_variables = {

        "current_data": str(state.attached_data),
        "history": state.history,
        "input": state.user_input,
        "langguage": state.langguage,
        "chain_data": state.chain_data
    }
    
    # 调用链处理用户最新输入
    chain_response = chain.invoke(prompt_variables)
    response_data = chain_response
    data = response_data.get("data")
    data["intent"] = state.detected_intent.value
    timestamp_time = time.time()
    print("使用 time 模块获取的 UTC 时间戳:", timestamp_time)
    data["timestamp"] = timestamp_time
    data["quoteResult"] = {}
    return state.copy(update={"result": data})
