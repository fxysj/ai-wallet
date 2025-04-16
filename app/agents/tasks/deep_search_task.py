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
def account_deep_asynic(selectedType,type_value):
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
    res =  send_get_request(url)
    if not res.get("error"):
        return res.get("result").get(contract_addresses[0])
    return {}

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

    res = send_get_request(url, headers=headers)
    if not res.get("error"):
        return res.get("data").get(symbol)
    return {}

#验证数据完整性
def validate_data(goPlusResult, symbolResult):
    required_goPlus_keys = ["chain", "creator_address", "creator_percent"]
    required_symbol_keys = ["name", "symbol", "price_usd"]

    for key in required_goPlus_keys:
        if key not in goPlusResult:
            raise KeyError(f"Missing key {key} in goPlusResult")

    for key in required_symbol_keys:
        if key not in symbolResult:
            raise KeyError(f"Missing key {key} in symbolResult")

#需要进行根据 goPlusResult  symbolResult 按照目的对象VO进行整合
#VOOverView
# 🧠 字段说明
#
# 字段名	来源	描述
# name, symbol, price_usd, market_cap_usd, volume_24h_usd	Symbol API	价格与市值信息
# creator_address, creator_percent, buy_tax, cannot_buy, cannot_sell_all	GoPlus API	链上安全性、创始人相关数据
# liquidity_pools	GoPlus API	DEX 上的流动性
# is_proxy	GoPlus API	是否为代理合约
# last_updated	Symbol API	数据更新时间
def uniongoPlusResultAndsymbolResultOverView(goPlusResult, symbolResult):
    """
        合并goPlusResult与symbolResult的字典数据，并进行合理的数据类型转换与默认值处理
    """
    def safe_get(d, key, default=None):
        return d.get(key, default)

    return {
        "name": safe_get(symbolResult, "name"),
        "symbol": safe_get(symbolResult, "symbol"),
        "token_address": safe_get(symbolResult, "token_address"),
        "chain": safe_get(goPlusResult, "chain"),
        "price_usd": safe_get(symbolResult, "price_usd"),
        "market_cap_usd": safe_get(symbolResult, "market_cap_usd"),
        "volume_24h_usd": safe_get(symbolResult, "volume_24h_usd"),
        "percent_change_24h": safe_get(symbolResult, "percent_change_24h"),
        "creator_address": safe_get(goPlusResult, "creator_address"),
        "creator_percent": safe_get(goPlusResult, "creator_percent"),
        "is_proxy": safe_get(goPlusResult, "is_proxy"),
        "buy_tax": safe_get(goPlusResult, "buy_tax"),
        "cannot_buy": safe_get(goPlusResult, "cannot_buy"),
        "cannot_sell_all": safe_get(goPlusResult, "cannot_sell_all"),
        "liquidity_pools": safe_get(goPlusResult, "dex", []),  # DEX 流动性信息，默认空列表
        "last_updated": safe_get(symbolResult, "last_updated")
    }

#需要进行根据 goPlusResult  symbolResult 按照目的对象VO进行整合
#VODetails
# 🔍 字段解释说明
# 🔐 risk_info（风险信息）
#
# 字段名	说明
# honeypot	是否为“蜜罐合约”，即买入可以但无法卖出，属于典型诈骗手法。
# slippage_modifiable	是否可修改滑点设置，可能用于操控交易滑点，影响用户交易成本。
# hidden_owner	合约是否隐藏了 owner（所有者）信息，可能存在操控风险。
# blacklisted	是否存在黑名单功能，可能对某些地址限制交易。
# mintable	合约是否可以增发（Mint），可能导致通胀、价格崩盘。
# transfer_pausable	合约是否可以暂停转账功能，可能影响代币流动性。
# proxy_contract	是否为代理合约结构，常用于合约升级，也可能隐藏逻辑。
# buy_tax	买入代币时收取的税率（%），如有较高税率应注意风险。
# sell_tax	卖出代币时收取的税率（%），如有较高税率应注意风险。
# creator_address	部署该合约的创作者地址。
# creator_percent	创作者持有该代币的比例（%），比例高风险集中。
# deployer_percent	部署者初始持仓占比（%），用于判断初期分布情况。
# holders	当前该代币的持有人数，用于判断分布是否集中。
# cannot_buy	是否禁止买入，常见于蜜罐合约。
# cannot_sell_all	是否无法一次性卖出全部资产，控制用户卖出权利。
# 🧊 dex_liquidity（DEX流动性）
# 是一个数组，结构可能如下：
#
# json
# 复制
# 编辑
# [
#   {
#     "dex": "Uniswap V2",
#     "pair": "TOKEN/USDT",
#     "liquidity_usd": 123456.78,
#     "pair_address": "0xabc...",
#     "last_updated": "2024-04-15T12:34:56Z"
#   }
# ]
#
# 字段名	说明
# dex	去中心化交易所名称（如 Uniswap、PancakeSwap）
# pair	交易对名称（如 TOKEN/USDT）
# liquidity_usd	当前交易对中的美元流动性金额
# pair_address	该交易对合约地址
# last_updated	数据最后更新时间
# 💰 symbol_info（币种基本信息）
#
# 字段名	说明
# symbol	代币符号（如 ETH、BTC）
# name	代币名称
# price_usd	当前价格（以美元计）
# percent_change_1h	过去 1 小时的价格涨跌幅（%）
# percent_change_24h	过去 24 小时的价格涨跌幅（%）
# percent_change_7d	过去 7 天的价格涨跌幅（%）
# volume_24h_usd	24 小时内交易量（美元）
# market_cap_usd	当前市场总市值（美元）
# circulating_supply	流通中的代币数量
# total_supply	代币总发行量
# max_supply	最大供应量（如果有限制）
# last_updated	数据更新时间戳
def uniongoPlusResultAndsymbolResultDetails(goPlusResult, symbolResult):
    return {
        "risk_info": {
            "honeypot": goPlusResult.get("is_honeypot"),
            "slippage_modifiable": goPlusResult.get("slippage_modifiable"),
            "hidden_owner": goPlusResult.get("hidden_owner"),
            "blacklisted": goPlusResult.get("blacklisted"),
            "mintable": goPlusResult.get("mintable"),
            "transfer_pausable": goPlusResult.get("transfer_pausable"),
            "proxy_contract": goPlusResult.get("is_proxy"),
            "buy_tax": goPlusResult.get("buy_tax"),
            "sell_tax": goPlusResult.get("sell_tax"),
            "creator_address": goPlusResult.get("creator_address"),
            "creator_percent": goPlusResult.get("creator_percent"),
            "deployer_percent": goPlusResult.get("deployer_percent"),
            "holders": goPlusResult.get("holders"),
            "cannot_buy": goPlusResult.get("cannot_buy"),
            "cannot_sell_all": goPlusResult.get("cannot_sell_all"),
        },
        "dex_liquidity": goPlusResult.get("dex", []),  # DEX 流动性池信息数组
        "symbol_info": {
            "symbol": symbolResult.get("symbol"),
            "name": symbolResult.get("name"),
            "price_usd": symbolResult.get("price_usd"),
            "percent_change_1h": symbolResult.get("percent_change_1h"),
            "percent_change_24h": symbolResult.get("percent_change_24h"),
            "percent_change_7d": symbolResult.get("percent_change_7d"),
            "volume_24h_usd": symbolResult.get("volume_24h_usd"),
            "market_cap_usd": symbolResult.get("market_cap_usd"),
            "circulating_supply": symbolResult.get("circulating_supply"),
            "total_supply": symbolResult.get("total_supply"),
            "max_supply": symbolResult.get("max_supply"),
            "last_updated": symbolResult.get("last_updated")
        }
    }


#其他类型API工具分析
def api_extra_asnyc(selectedType,type_value):
    chain_id = selectedType.get("chain_id")
    contract_addresses = selectedType.get("contract_addresses")
    symbol= selectedType.get("symbol")
    #goPlusResult
    goPlusResult = GoPlusAPISearch(chain_id, contract_addresses)
    #symbolResult
    symbolResult = SymbolAPISearch(symbol)
    symbolResult = symbolResult[0] #只取第一个数组数据
    response = {}
    response["overview"] = uniongoPlusResultAndsymbolResultOverView(goPlusResult,symbolResult)
    response["details"] =uniongoPlusResultAndsymbolResultDetails(goPlusResult,symbolResult)
    response["type"] = type_value
    response["state"] =  TaskState.RESEARCH_TASK_DISPLAY_RESEARCH
    return response

#默认返回处理函数
def default_deal_with(selectedType,type_value):
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
        detail_data = getDetailRowdata(type_item)
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
        return api_extra_asnyc(type_item,type_value)
    elif type_value == 1:
        return account_deep_asynic(type_item,type_value)

    else:
        # 默认：不支持的类型，清空数据结构
        return default_deal_with(type_item,type_value)


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

def getDetailRowdata(selectedType):
    if not selectedType or not selectedType.get("id"):
        return {}
    id = selectedType.get('id')  # 项目id
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
    #如果没有错误返回
    if not result.get("error"):
        return result.get("data",{})
    return {}



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
        # 只处理 type 为 1, 2, 3, 4 的项
        if item_type not in [1, 2, 3, 4]:
            continue

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
            "description":"I have confirmed the information to be queried. Kindly assist in retrieving the relevant data",
            "overview": handled_result.get("overview", {}),
            "details": handled_result.get("details", {}),
            "state": handled_result.get("state", ""),
        })
        return state.copy(update={"result": data})

    # 情况一：attached_data 存在
    if state.attached_data:
        selected_type = state.attached_data.get("selectedType")
        data = state.attached_data if selected_type else None

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









# if __name__ == '__main__':
#     test_data = {
#         'intent': 'deep_research',
#         'form': {
#             'query': 'Official Trump',
#             'selectedProject': {
#                 'introduce': 'Official Trump is a meme coin issued on the Solana blockchain.',
#                 'name': 'Official Trump',
#                 'logo': 'https://public.rootdata.com/images/b13/1737172225426.jpg',
#                 'active': True,
#                 'rootdataurl': 'https://www.rootdata.com/Projects/detail/Official Trump?k=MTU5Mjc=',
#                 'id': 15927,
#                 'type': 1
#             }
#         },
#         'typeList': [{'id': 15927, 'type': 1}]
#     }
#     result = getDetailRowdata(test_data)
#     print("详细数据：", result)
#     overview_result = OverView(result)
#     print("大模型概述：", overview_result)

if __name__ == '__main__':
    # result = SymbolAPISearch("SHIB")
    # print(result[0])
    # res=searchRowData("ETH")
    # res= getDetailRowdata({
    #     "id":15927
    # })
    # print(res)
    # print(res)
    res =api_extra_asnyc({
        "chain_id":56,
        "contract_addresses": ["0xba2ae424d960c26247dd6c32edc70b295c744c43"],
        "symbol": "SHIB"
    },3)
    print(res)
    # res=GoPlusAPISearch(56,["0xba2ae424d960c26247dd6c32edc70b295c744c43"])
    # print(res)