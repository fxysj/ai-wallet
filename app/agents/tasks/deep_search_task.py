#深度搜索分析
import asyncio
import time
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.form.form import TaskState
from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.deepSearchTask_prompt_en import DEEPSEARCHTASK_PROMPT
from app.agents.proptemts.overview_asnsy_propmt import OVERVIEW_ASNYC_PROPMT
from app.agents.schemas import AgentState
from app.agents.tools import send_post_request
from app.agents.lib.redisManger.redisManager import redis_dict_manager

#获取rawData数据s
#根据详情信息返回OverView数据
def wrap_del_with_detail(detail_data):
    return {}


def handle_type_based_data(type_item, attached_data):
    """
    根据项目类型处理不同逻辑
    """
    type_value = type_item.get("type")

    if type_value in [2, 3]:
        # 走 getDetailRowdata 查询
        detail_data = getDetailRowdata(attached_data)
        if detail_data:
            return {
                "overview": wrap_del_with_detail(detail_data),
                "details": detail_data,
                "state": TaskState.RESEARCH_TASK_DISPLAY_RESEARCH
            }

    elif type_value == 4:
        # 调用其他API处理（示例逻辑）
        # 你可以定义自己的函数 fetch_type4_data()
        return {
            "overview": {"note": "暂不支持的类型，需接入新的接口"},
            "details": {},
            "state": "TYPE4_PENDING"
        }

    else:
        # 默认：不支持的类型，清空数据结构
        return {
            "overview": {},
            "details": {},
            "state": ""
        }


# 封装后的searchResult函数
def searchResult(attached_data):
    # 从attached_data中获取selectedProject
    #selected_project = attached_data.get('form', {}).get('selectedProject')
    # 设置API的url和headers
    url = ""
    headers = {
        "apikey": "UvO5c6tLGHZ3a5ipkPZsXDbOUYRiKUgQ",
        "language": "en",
        "Content-Type": "application/json"
    }
    # 没有selectedProject，调用ser_inv API
    url = "https://api.rootdata.com/open/ser_inv"
    query = attached_data.get('form', {}).get('query', "ETH")  # 默认查询 ETH
    payload = {
            "query": query
        }
    # 使用工具函数发起请求
    return send_post_request(url, payload, headers)

def getDetailRowdata(attached_data):
    data = attached_data.get('typeList', {})
    if not data:
        return {}
    selectedProject = data[0]
    if not selectedProject:
        return {}
    id = selectedProject.get('id')  # 项目id
    headers = {
        "apikey": "UvO5c6tLGHZ3a5ipkPZsXDbOUYRiKUgQ",
        "language": "en",
        "Content-Type": "application/json"
    }
    # 没有selectedProject，调用ser_inv API
    url = "https://api.rootdata.com/open/get_item"
    payload = {
        "project_id": id,
        "include_team": True,
        "include_investors": True,
    }
    # 使用工具函数发起请求
    result = send_post_request(url, payload, headers)
    return result

#根据选择的获取详情信息
def OverView(result):
    if not result:
        return result
    #这个是项目返回的数据 需要调用大模型进行生成
    llm = LLMFactory.getDefaultOPENAI()
    prompt = PromptTemplate(
        template=OVERVIEW_ASNYC_PROPMT,
        input_variables=["data"],
    )
    chain = prompt | llm | JsonOutputParser()
    # 调用链处理用户最新输入
    chain_response =  chain.invoke({
        "data": str(result),
    })
    return  chain_response


def Details(attached_data):
    return {}


async def async_getDetailRowdata(attached_data):
    """异步获取项目信息"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, getDetailRowdata, attached_data)


async def async_OverView(detailData):
    """异步调用大模型生成概述"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, OverView, detailData)


async def process_research_data(state: AgentState, data,progress_key):
    """后台任务：获取详情和大模型结果，然后存入 Redis"""
    # 初始化 Redis 数据（包含进度和业务数据）
    redis_dict_manager.add(progress_key, {"progress": 10, "message": "Task started", "data": data})

    # 进度 40%：开始获取项目信息
    redis_dict_manager.add(progress_key, {"progress": 40, "message": "Fetching project details...", "data": data})
    # 获取详细数据（异步）
    detailData = await async_getDetailRowdata(state.attached_data)


    # 进度 70%：调用大模型生成概述
    redis_dict_manager.add(progress_key, {"progress": 70, "message": "Generating project overview...", "data": data})

    # 调用大模型获取项目概述（异步）
    res = await async_OverView(detailData)

    if res:
        data["overview"] = res["overview"]
        data["details"] = res["details"]
        data["details"]["rootDataResult"] = detailData
        data["state"] = TaskState.RESEARCH_TASK_DISPLAY_RESEARCH
        # 进度 90%：数据整合完成
        redis_dict_manager.add(progress_key, {"progress": 90, "message": "Finalizing data...", "data": data})

 # 进度 100%：任务完成
    redis_dict_manager.add(progress_key, {"progress": 100, "message": "Task completed", "data": data})

async def research_task(state: AgentState) -> AgentState:
    print("research_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    prompt = PromptTemplate(
        template=DEEPSEARCHTASK_PROMPT,
        input_variables=["current_data", "history", "input", "langguage"],
    )
    llm = LLMFactory.getDefaultOPENAI()
    chain = prompt | llm | JsonOutputParser()
    # 调用链处理用户最新输入
    chain_response = chain.invoke({
        "current_data": str(state.attached_data),
        "history": state.history,
        "input": state.user_input,
        "langguage": state.langguage
    })
    response_data = chain_response
    print("deep_sarch_data")
    data = response_data.get("data")
    data["intent"] = state.detected_intent.value
    # 使用 time 模块获取当前时间戳
    timestamp_time = time.time()
    print("使用 time 模块获取的 UTC 时间戳:", timestamp_time)
    data["timestamp"] = state.attached_data.get("timestamp", timestamp_time)
    #获取对应的
    missField = data["missFields"]
    if missField:
        return state.copy(update={"result": data})

    typeList = state.attached_data.get("typeList")
    typeSelected = typeList[0]


    handled_result = handle_type_based_data(typeSelected, state.attached_data)
    data["overview"] = handled_result.get("overview")
    data["details"] = handled_result.get("details")
    data["state"] = handled_result.get("state")
    return state.copy(update={"result": data})



if __name__ == '__main__':
    data = {'intent': 'deep_research', 'form': {'query': 'Official Trump', 'selectedProject': {'introduce': 'Official Trump is a meme coin issued on the Solana blockchain, introduced by the elected U.S. president Donald Trump through a social media post.', 'name': 'Official Trump', 'logo': 'https://public.rootdata.com/images/b13/1737172225426.jpg', 'active': True, 'rootdataurl': 'https://www.rootdata.com/Projects/detail/Official Trump?k=MTU5Mjc=', 'id': 15927, 'type': 1}}}
    res = getDetailRowdata(data)
    #print(res)
    rest = OverView(res)
    print(rest)