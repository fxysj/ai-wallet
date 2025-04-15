import unittest
from app.agents.lib.llm.llm import LLMFactory
from app.agents.tools import send_post_request
from app.test.deepSearchProject.deepSearchTask_prompt_test import DEEPSEARCHTASK_PROMPT_TEST
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
def generate_chain():
    llm = LLMFactory.getDefaultDeepSearchOPENAI()
    prompt = PromptTemplate(
        template=DEEPSEARCHTASK_PROMPT_TEST,
        input_variables=["current_data", "history", "input", "langguage", "chain_data"],
    )
    return prompt | llm | JsonOutputParser()

def run_deep_search_test(input_text, current_data=None, history=None, langguage="cn"):
    print("========= DEEP SEARCH TEST INPUT =========")
    print(f"Input: {input_text}")
    print("==========================================")
    if current_data is None:
        current_data = {}
    if history is None:
        history = []

    chain = generate_chain()
    result = chain.invoke({
        "current_data": current_data,
        "history": history,
        "input": input_text,
        "language": langguage
    })

    print("=============== RESULT ===================")
    print(result)
    print("==========================================")
    data = result.get("data")
    data["typeList"] = wrapListInfo(data.get("typeList"))
    result["data"] = data

    print("============ RESULTWrap ====================")
    print(result)
    return result

# {
# 	'data': {
# 		'description': '请确认以下项目是否为您要查找的目标，如需更准确匹配，请补充关键词。',
# 		'timestamp': 1713140339.0,
# 		'state': 'RESEARCH_TASK_DISPLAY_PROMPTED_PROJECT',
# 		'form': {
# 			'query': 'BSC'
# 		},
# 		'typeList': [{
# 			'id': 'type2_bnb-smart-chain',
# 			'title': 'BNB 智能链（原称 BSC）',
# 			'logo': 'https://api.rootdata.com/uploads/public/b15/1666341829033.jpg',
# 			'type': 2,
# 			'detail': 'BNB 智能链（BNB Smart Chain，原称 BSC）是由币安于 2020 年推出的区块链网络，旨在提供高性能的去中心化应用程序（DApp）平台。该链支持智能合约功能，并与以太坊虚拟机（EVM）兼容，方便开发者将项目从以太坊迁移至 BNB 智能链。BNB 智能链采用权威权益证明（PoSA）共识机制，出块时间约为 3 秒，验证者通过质押 BNB 参与网络共识并获得交易手续费作为奖励。 ([academy.binance.com](https://academy.binance.com/zh-CN/articles/an-introduction-to-bnb-smart-chain-bsc?utm_source=openai))',
# 			'chain_id': 56,
# 			'contract_addresses': []
# 		}],
# 		'missFields': []
# 	}
# }


# 'typeList': [{
#     'id': 'type2_bnb-smart-chain',
#     'title': 'BNB 智能链（原称 BSC）',
#     'logo': 'https://api.rootdata.com/uploads/public/b15/1666341829033.jpg',
#     'type': 2,
#     'detail': 'BNB 智能链（BNB Smart Chain，原称 BSC）是由币安于 2020 年推出的区块链网络，旨在提供高性能的去中心化应用程序（DApp）平台。该链支持智能合约功能，并与以太坊虚拟机（EVM）兼容，方便开发者将项目从以太坊迁移至 BNB 智能链。BNB 智能链采用权威权益证明（PoSA）共识机制，出块时间约为 3 秒，验证者通过质押 BNB 参与网络共识并获得交易手续费作为奖励。 ([academy.binance.com](https://academy.binance.com/zh-CN/articles/an-introduction-to-bnb-smart-chain-bsc?utm_source=openai))',
#     'chain_id': 56,
#     'contract_addresses': []
# }],
#根据关键词查询rowdata中的项目和VC信息
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

#根据项目的具体的id查询出对应的详情信息

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
            search_result = searchRowData(title)
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






def test_case_1_basic_search():
    run_deep_search_test("0x980DD1c27614121231F5A64Db9DD7c679C3551d2")


def test_case_2_modify_input():
    run_deep_search_test("我要查的是 BIT")


def test_case_3_missing_fields():
    run_deep_search_test("帮我查一下 Root")


def test_case_4_wrong_type_fix():
    run_deep_search_test("上次你查的是 Uniswap 协议，但我要找的是 Uniswap 的地址")


def test_case_5_english_environment():
    run_deep_search_test("SushiSwap", langguage="en")


def test_case_6_fully_filled_ready_search():
    run_deep_search_test("我找的是 Aave 协议，不是 Token，快点开始吧！")

if __name__ == '__main__':
    #test_case_1_basic_search()
    test_case_2_modify_input()
    # test_case_3_missing_fields()
    # test_case_4_wrong_type_fix()
    # test_case_5_english_environment()
    # test_case_6_fully_filled_ready_search()