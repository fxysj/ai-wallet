#深度搜索分析
import asyncio
import time
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.form.form import TaskState
from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.overview_asnsy_propmt import OVERVIEW_ASNYC_PROPMT
from app.agents.schemas import AgentState
from app.agents.tools import send_post_request, send_get_request
from app.agents.lib.redisManger.redisManager import redis_dict_manager
from app.test.deepSearchProject.deepSearchTask_prompt_test import DEEPSEARCHTASK_PROMPT_TEST


#获取rawData数据s
#根据详情信息返回OverView数据
def wrap_del_with_detail(detail_data):
    return detail_data

#账号深度分析
def account_deep_asynic(attached_data,type_value):
    return {
        "overview": {},
        "details": {},
        "state": TaskState.RESEARCH_TASK_DISPLAY_RESEARCH,
        "type": "",
    }

#根据chain_id contract_addresses
#合约地址 请求:
#https://api.gopluslabs.io/api/v1/token_security/56?contract_addresses=0xba2ae424d960c26247dd6c32edc70b295c744c43&

def GoPlusAPISearch(chain_id, contract_addresses):
    """
    调用 GoPlusLabs Token Security API 查询合约地址的安全性信息

    :param chain_id: int 链ID（如56为BSC）
    :param contract_addresses: List[str] 合约地址列表
    :return: dict 请求返回的数据
    """
    if not contract_addresses:
        return {"error": "contract_addresses 不能为空"}

    # 合并地址列表为逗号分隔字符串
    contract_param = ",".join(contract_addresses)

    # 构造 URL
    url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}?contract_addresses={contract_param}"

    # 发起 GET 请求（使用你封装的工具函数）
    return send_get_request(url)

#https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?symbol=SHIB
#根据代币的名称查询
#需要头部参数:X-CMC_PRO_API_KEY:[{"key":"X-CMC_PRO_API_KEY","value":"d2cf066b-ca89-4266-a580-e6733c044aa1","description":"","type":"text","uuid":"11faf309-a41e-4dbb-ba86-5ddc3aee9024","enabled":true}]
def SymbolAPISearch(symbol):
    """
    根据代币名称（symbol）查询 CoinMarketCap 最新报价

    :param symbol: str 代币名称（如 SHIB, BTC, ETH）
    :return: dict 返回报价信息或错误信息
    """
    url = f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?symbol={symbol}"

    headers = {
        "X-CMC_PRO_API_KEY": "d2cf066b-ca89-4266-a580-e6733c044aa1"
    }

    return send_get_request(url, headers=headers)




#其他类型API工具分析
def api_extra_asnyc(attached_data,type_value):
    pass

#默认返回处理函数
def default_deal_with(attached_data,type_value):
    return {
        "overview": {},
        "details": {},
        "state": TaskState.RESEARCH_TASK_DISPLAY_RESEARCH,
        "type": "",
    }


def EmptyResult():
    return  {
        "overview": {},
        "details": {},
        "state": TaskState.RESEARCH_TASK_DISPLAY_RESEARCH,
        "type":"",
    }


def handle_type_based_data(type_item, attached_data):
    """
    根据项目类型处理不同逻辑
    """
    #如果为空则默认返回空的结构
    if not  type_item:
        return EmptyResult()
    #如果不为空则进行根据type整合数据
    type_value = type_item.get("type")

    if type_value in [2, 4]:
        # 走 getDetailRowdata 查询
        detail_data = getDetailRowdata(attached_data)
        if detail_data:
            return {
                "overview": wrap_del_with_detail(detail_data),
                "details": detail_data,
                "state": TaskState.RESEARCH_TASK_DISPLAY_RESEARCH,
                "type":type_value
            }

    elif type_value == 3:
        # 调用其他API处理（示例逻辑）
        # 你可以定义自己的函数 fetch_type4_data()
        return api_extra_asnyc(attached_data,type_value)
    elif type_value == 1:
        return account_deep_asynic(attached_data,type_value)

    else:
        # 默认：不支持的类型，清空数据结构
        return default_deal_with(attached_data,type_value)


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
    data = attached_data.get('selectedType',{})
    if not data:
        return {}

    selected_project = data
    if not selected_project or not selected_project.get("id"):
        return {}
    id = selected_project.get('id')  # 项目id
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

#返回类型项目和VC列表信息
def searchRowData(query):
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
    payload = {
            "query": query
        }
    # 使用工具函数发起请求
    return send_post_request(url, payload, headers)


#需要根据返回的typelist进行优化处理
def wrapListInfo(typelist):
    new_list = []

    for item in typelist:
        item_type = item.get("type")
        if item_type in [2, 4]:
            title = item.get("title")
            if not title:
                new_list.append(item)
                continue

            # 调用 searchRowData，并取第一条结果
            search_result = searchRowData(title).get("data")
            if isinstance(search_result, list) and len(search_result) > 0:
                first_data = search_result[0]

                # 创建新项，保留原有字段，只替换指定字段
                updated_item = item.copy()
                updated_item.update({
                    "id": first_data.get("id"),
                    "title": first_data.get("name"),
                    "logo": first_data.get("logo"),
                    "detail": first_data.get("introduce")  # 用 introduce 替换 detail
                })

                new_list.append(updated_item)
            else:
                # 如果返回不合法，就保留原始
                new_list.append(item)
        else:
            new_list.append(item)

    return new_list

async def research_task(state: AgentState) -> AgentState:
    print("research_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)

    def call_llm_chain(state: AgentState):
        prompt = PromptTemplate(
            template=DEEPSEARCHTASK_PROMPT_TEST,
            input_variables=["current_data", "history", "input", "langguage"],
        )
        llm = LLMFactory.getDefaultDeepSearchOPENAI()
        chain = prompt | llm | JsonOutputParser()
        return chain.invoke({
            "current_data": str(state.attached_data),
            "history": state.history,
            "input": state.user_input,
            "language": state.langguage
        })

    def update_result_with_handling(data: dict, state: AgentState) -> AgentState:
        data["intent"] = state.detected_intent.value
        timestamp_time = time.time()
        print("使用 time 模块获取的 UTC 时间戳:", timestamp_time)
        data["timestamp"] = state.attached_data.get("timestamp", timestamp_time)
        selectedType = state.attached_data.get("selectedType", {})
        handled_result = handle_type_based_data(selectedType, state.attached_data)
        data.update({
            "overview": handled_result.get("overview", {}),
            "details": handled_result.get("details", {}),
            "state": handled_result.get("state", ""),
        })
        return state.copy(update={"result": data})

    # 情况一：attached_data 存在
    if state.attached_data:
        selected_type = state.attached_data.get("selectedType")
        data = state.attached_data.get("data") if selected_type else None

        if not selected_type:
            print("未选择 selectedType，调用 LLM...")
            response_data = call_llm_chain(state)
            print("deep_search_data")
            data = response_data.get("data", {})
            if data.get("missFields"):
                data["intent"] = state.detected_intent.value
                timestamp_time = time.time()
                data["timestamp"] = state.attached_data.get("timestamp", timestamp_time)
                return state.copy(update={"result": data})

            # 对 LLM 返回的数据进行处理
            data["typeList"] = wrapListInfo(data.get("typeList"))
        return update_result_with_handling(data, state)

    # 情况二：attached_data 不存在，同样调用 LLM
    print("attached_data 不存在，调用 LLM...")
    response_data = call_llm_chain(state)
    print("deep_search_data")
    data = response_data.get("data", {})
    if data.get("missFields"):
        data["intent"] = state.detected_intent.value
        timestamp_time = time.time()
        data["timestamp"] = time.time()
        return state.copy(update={"result": data})

    data["typeList"] = wrapListInfo(data.get("typeList"))
    return update_result_with_handling(data, state)









if __name__ == '__main__':
    test_data = {
        'intent': 'deep_research',
        'form': {
            'query': 'Official Trump',
            'selectedProject': {
                'introduce': 'Official Trump is a meme coin issued on the Solana blockchain.',
                'name': 'Official Trump',
                'logo': 'https://public.rootdata.com/images/b13/1737172225426.jpg',
                'active': True,
                'rootdataurl': 'https://www.rootdata.com/Projects/detail/Official Trump?k=MTU5Mjc=',
                'id': 15927,
                'type': 1
            }
        },
        'typeList': [{'id': 15927, 'type': 1}]
    }
    result = getDetailRowdata(test_data)
    print("详细数据：", result)
    overview_result = OverView(result)
    print("大模型概述：", overview_result)

if __name__ == '__main__':
    # result = SymbolAPISearch("SHIB")
    # print(result)
    # res=searchRowData("ETH")
    res= getDetailRowdata({"selectedType": {
        "id":15927
    }})
    print(res)
    # print(res)
    # res=GoPlusAPISearch(56,["0xba2ae424d960c26247dd6c32edc70b295c744c43"])
    # print(res)