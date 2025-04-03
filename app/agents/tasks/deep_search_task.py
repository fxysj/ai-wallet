#深度搜索分析
import json
import time
from math import trunc

import requests
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.form.form import TaskState
from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.deepSearchTask_prompt import DEEPSEARCHTASK_PROMPT
from app.agents.proptemts.overview_asnsy_propmt import OVERVIEW_ASNYC_PROPMT
from app.agents.schemas import AgentState
from app.agents.tools import send_post_request
from app.agents.lib.redisManger.redisManager import redis_dict_manager

#获取rawData数据s

# 封装后的searchResult函数
def searchResult(attached_data):
    # 从attached_data中获取selectedProject
    #selected_project = attached_data.get('form', {}).get('selectedProject')
    # 设置API的url和headers
    url = ""
    headers = {
        "apikey": "43qiBs947TKm0UNDbZ0gQz5ZTHaPpp8Y",
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
    data = attached_data.get('form', {})
    if not data:
        return {}
    selectedProject = data.get("selectedProject")
    if not selectedProject:
        return {}
    id = selectedProject.get('id')  # 项目id
    headers = {
        "apikey": "43qiBs947TKm0UNDbZ0gQz5ZTHaPpp8Y",
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
    #获取对应的深度搜索的结果响应
    searchData= searchResult(state.attached_data)
    #detailData
    detailData = getDetailRowdata(state.attached_data)
    data["promptedProject"]= searchData.get("data",[])
    res = OverView(detailData)
    if res:
        data["overview"] = res["overview"]
        data["details"] = res["details"]
        data["details"]["rootDataResult"] = detailData
        data["state"]= TaskState.RESEARCH_TASK_DISPLAY_RESEARCH
        key = "research:"+state.session_id
        print(key)
        redis_dict_manager.add(key,data)
    if state.attached_data:
        data["form"] = state.attached_data.get("form")

    return state.copy(update={"result": data})

if __name__ == '__main__':
    data = {'intent': 'deep_research', 'form': {'query': 'Official Trump', 'selectedProject': {'introduce': 'Official Trump is a meme coin issued on the Solana blockchain, introduced by the elected U.S. president Donald Trump through a social media post.', 'name': 'Official Trump', 'logo': 'https://public.rootdata.com/images/b13/1737172225426.jpg', 'active': True, 'rootdataurl': 'https://www.rootdata.com/Projects/detail/Official Trump?k=MTU5Mjc=', 'id': 15927, 'type': 1}}}
    res = getDetailRowdata(data)
    #print(res)
    rest = OverView(res)
    print(rest)