#深度搜索分析
import asyncio
import json
import time
from decimal import Decimal, getcontext

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.emun.LanguageEnum import LanguageEnum
from app.agents.form.form import TaskState
from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.overview_asnsy_propmt import OVERVIEW_ASNYC_PROPMT
from app.agents.schemas import AgentState, Intention
from app.agents.tools import send_post_request, send_get_request
from app.agents.lib.redisManger.redisManager import redis_dict_manager
from app.test.deepSearchProject.deepSearchTask_prompt_test import DEEPSEARCHTASK_PROMPT_TEST
from app.agents.tasks.deep_search_task_language import EnumValueRegistry

def truncate_link(link):
    """
    截断链接为前8后6字符，中间以'...'连接，链接长度不足15则不处理
    """
    if not isinstance(link, str) or len(link) <= 14:
        return link
    return f"{link[:8]}...{link[-6:]}"

def format_team_links(team_members):
    """
    批量处理团队成员的X链接和LinkedIn链接，进行美化展示
    """
    if not isinstance(team_members, list) or not team_members:
        return []

    for member in team_members:
        if not isinstance(member, dict):
            continue  # 跳过非法格式

        if "linkedin" not in member:
            member['linkedin'] = "--"

    return team_members


#处理报告信息
from datetime import datetime
def process_reports(reports):
    if not isinstance(reports, list) or len(reports) == 0:
        return []

    def parse_time(report):
        try:
            return datetime.fromisoformat(report.get("time_east", ""))
        except Exception:
            return datetime.min  # 解析失败放最末尾

    # 排序（时间倒序）
    sorted_reports = sorted(reports, key=parse_time, reverse=True)

    # 提取指定字段
    result = [
        {
            "title": report.get("title", ""),
            "url": report.get("url", ""),
            "time_east": report.get("time_east", "")
        }
        for report in sorted_reports
    ]

    return result
#处理事件信息
from datetime import datetime
def sort_events(events):
    if not isinstance(events, list) or len(events) == 0:
        return []

    def parse_time(item):
        try:
            return datetime.fromisoformat(item.get("hap_date", ""))
        except Exception:
            return datetime.min  # 无法解析的时间排到最后

    # 按时间降序排序
    sorted_events = sorted(events, key=parse_time, reverse=True)

    # 保留指定字段
    result = [
        {
            "hap_date": item.get("hap_date", ""),
            "event": item.get("event", "")
        }
        for item in sorted_events
    ]

    return result

def add_discord_if_missing(info_dict):
    if not isinstance(info_dict, dict):
        return info_dict
    # 空字典直接返回
    if len(info_dict) == 0:
        return info_dict
    # 不存在discord字段则添加
    if "discord" not in info_dict:
        info_dict["discord"] = "--"
    return info_dict

#获取rawData数据s
#根据详情信息返回OverView数据
def wrap_del_with_detail(detail_data,langguage):
    price = detail_data.get("price", "")
    if not price:
        price = 0.0

    fdv = detail_data.get("fully_diluted_market_cap", "")
    if not fdv:
        fdv = 0

    MCap = detail_data.get("market_cap", "")
    if not MCap:
        MCap = 0

    total_funding = detail_data.get("total_funding", "")
    if not total_funding:
        total_funding = 0

    followers = detail_data.get("followers", "")
    if not followers:
        followers = 0

    from app.utuls.format_price_display import format_price_display_project
    calute_price = format_price_display_project(float(price))
    return format_and_convert_keys({
        "Project_Name": detail_data.get("project_name", ""),
        "logo": detail_data.get("logo", ""),
        "Token_Symbol": detail_data.get("token_symbol", ""),
        "Token_Price": calute_price,
        "FDV": format_number(fdv),
        "M.Cap": format_number(MCap),
        "Brief": detail_data.get("one_liner", ""),
        "Fundraising_Amount": format_number(total_funding),
        "Ecosystem": detail_data.get("ecosystem", ""),
        "X_Followers": format_number(followers),
        "Description": detail_data.get("description"),
        "Reports":process_reports(detail_data.get("reports",[])),
        "Events":sort_events(detail_data.get("event",[])),
        "investors":detail_data.get("investors",[]),
        "Team_Member":format_team_links(detail_data.get("team_members",[])),
        "Social_Media":add_discord_if_missing(filter_empty_values(detail_data.get("social_media",{})))
    })



#账号深度分析
def account_deep_asynic(selectedType,type_value,langguage):
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
        result = res.get("result")
        if result:
            print("goplusrusult:===", result)
            contract_address = contract_addresses[0]
            print("contract_address:===", contract_address)
            print("type(goplusrusult):===", type(result))
            # 0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE
            print("你请求的地址（小写）:", contract_address.lower())
            response = result.get(contract_address.lower())
            print("response:===", response)
            return response
        else:
            return {}
    else:
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
    symbol_upper = symbol.upper()
    print("res:")
    print(res)
    if not res.get("error"):
        return res.get("data").get(symbol_upper)
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


def sum_top_10_balances(data):
    # 将字符串 balance 转为 Decimal 并排序（从高到低）
    sorted_data = sorted(data, key=lambda x: Decimal(x["balance"]), reverse=True)

    # 取前十名并求和
    total = sum(Decimal(item["balance"]) for item in sorted_data[:10])

    # 保留两位小数返回
    return round(total, 2)
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
def sum_top10_holders_ratio(data):
    # 将字符串 balance 转为 Decimal 并排序（从高到低）
    sorted_data = sorted(data, key=lambda x: Decimal(x["percent"]), reverse=True)

    # 取前十名并求和
    total = sum(Decimal(item["percent"]) for item in sorted_data[:10])

    # 保留两位小数返回
    return round(total, 2)


def format_number(num):
    try:
        num = float(num)
    except (ValueError, TypeError):
        # 不能转换成浮点数的，直接返回字符串形式
        return str(num)

    abs_num = abs(num)

    if abs_num < 1_000:
        return f"{num:.2f}"
    elif abs_num < 1_000_000:
        return f"{num / 1_000:.2f}K"
    elif abs_num < 1_000_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif abs_num < 1_000_000_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    else:
        return f"{num / 1_000_000_000_000_000:.2f}P"


def format_string(s):
    if len(s) <= 10:
        return s
    return s[:4] + '***' + s[-6:]

def filter_empty_values(info_dict):
    for key, value in info_dict.items():
        if value is None or (isinstance(value, str) and value.strip() == ""):
            info_dict[key] = "--"
    return info_dict

def uniongoPlusResultAndsymbolResultOverView(goPlusResult, CMCResult,Contract_Address="",langguage=""):
    """
        合并goPlusResult与symbolResult的字典数据，并进行合理的数据类型转换与默认值处理
    """
    def safe_get(d, key, default=None):
        return d.get(key, default)

    max_supply = safe_get(CMCResult, "max_supply")
    price = safe_get(CMCResult, "quote")
    if not price:
        price = 0.0
    else:
        price = price.get("USD").get("price")

    if max_supply is not None and price is not None:
        fdv = max_supply * price
    else:
        fdv = 0.0  # 或者 None，根据你的业务需求决定

    circulating_supply = safe_get(CMCResult, "circulating_supply")
    mcap = (circulating_supply or 0) * (price or 0)

    max_supply=safe_get(CMCResult, "max_supply")
    if not max_supply:
        max_supply=0

    circulating_supply= safe_get(CMCResult, "circulating_supply")

    token_symbol=safe_get(goPlusResult,"token_symbol")

    creator_address= safe_get(goPlusResult,"creator_address")
    owner_address=safe_get(goPlusResult,"owner_address")
    holder_count=safe_get(goPlusResult,"holder_count")
    # 设置高精度以确保中间计算准确
    getcontext().prec = 28
    #计算前十holders信息余额信息
    top10Banlance = sum_top_10_balances(safe_get(goPlusResult,"holders"))
    top10_holders_ratio = sum_top10_holders_ratio(safe_get(goPlusResult,"holders"))
    #引入格式化TokenPrice 进行展示的人物
    from app.utuls.format_price_display import format_price_display
    calute_price = format_price_display(price)
    deep_research_report_basic = {
        "Token_Price": calute_price,
        "FDV": format_number(fdv),
        "M.Cap": format_number(mcap),
        "Max_Supply": format_number(max_supply),
        "Circulation": format_number(circulating_supply),
        "Token_Symbol": token_symbol,
        "Contract_Address": Contract_Address,  # 按照前四后六进行展示
        "Contract_Creator": creator_address,  # 按照前四后六进行展示
        "Contract_Owner": owner_address,  # 按照前四后六进行展示
        "Toker_Holders": holder_count,  # 统计风险项和注意项的总数。
        "Token_Supply": format_number(float(top10Banlance)),  # 保留小数点后两位展示。直接展示真实数字，不需要进行k m b单位换算。
        "Top10_Holders_Ratio": str(top10_holders_ratio * 100) + "%",  # 保留小数点后两位并采用百分比展示。
        "AttentionItem": 0,  # 注意事项
        "RiskyItem": 0,  # 风险事项
    }
    #展示价格方式
    basic_info = {
        "basic_info": deep_research_report_basic,  # 基础信息
    }
    #组织返回基础信息
    return format_and_convert_keys(basic_info)


def count_risks_filtered(security_list, *, risk_level="Risky"):
    """
    过滤掉非 dict 的无效项，并统计指定 riskLevel 中 risked 为 True 的项数量。
    同时根据条件添加 color_type 字段：
        - riskLevel == "Risky" 且 risked=True -> color_type = 1（红色）
        - riskLevel == "Attention" 且 risked=True -> color_type = 2（黄色）
        - 其他情况 -> color_type = 3（默认）

    :param security_list: 合约安全项列表
    :param risk_level: 指定要统计的风险等级，默认为 "Risky"
    :return: (filtered_list, risk_count)
    """
    filtered_list = []
    risk_count = 0

    for item in security_list:
        if isinstance(item, dict):
            # 判断 color_type
            if item.get("risked") is True and item.get("riskLevel") == "Risky":
                item["color_type"] = 1  # 红色
            elif item.get("risked") is True and item.get("riskLevel") == "Attention":
                item["color_type"] = 2  # 黄色
            else:
                item["color_type"] = 3  # 默认

            filtered_list.append(item)

            # 统计指定 risk_level 中 risked 为 True 的数量
            if item.get("risked") is True and item.get("riskLevel") == risk_level:
                risk_count += 1

    return filtered_list, risk_count




def filter_valid_security_items(security_list):
    """
    过滤掉非字典类型的项，以及缺少 title/description/value 的字典。

    :param security_list: 原始的 contractSecurity 列表
    :return: 过滤后的有效安全项列表
    """
    if not isinstance(security_list, list):
        return []

    return [
        item for item in security_list
        if isinstance(item, dict)
           and all(k in item for k in ("title", "description", "value"))
    ]


def format_percentage(value, decimals=0):
    """
    将数值格式化为百分比字符串。
    例如：0.15 -> "15%"，保留 `decimals` 位小数。
    """
    try:
        percent_value = float(value) * 100
        format_str = f"{{:.{decimals}f}}%"
        return format_str.format(percent_value)
    except (ValueError, TypeError):
        return ""

def format_liquidity_data(data):
    def format_liquidity(value):
        num = round(float(value), 2)
        if num < 1_000:
            return f"{num:.2f}"
        elif num < 1_000_000:
            return f"{num / 1_000:.2f}K"
        elif num < 1_000_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif num < 1_000_000_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        else:
            return f"{num / 1_000_000_000_000_000:.2f}P"

    def shorten_address(addr):
        if len(addr) < 20:
            return addr
        return addr[:10] + "..." + addr[-10:]

    result = []
    for item in data:
        formatted = {
            "liquidity_type": item.get("liquidity_type", ""),
            "name": item.get("name", ""),
            "liquidity": format_liquidity(item.get("liquidity", "0")),
            "pair": shorten_address(item.get("pair", ""))
        }
        result.append(formatted)

    return result


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
def uniongoPlusResultAndsymbolResultDetails(goPlusResult, CMCResult,Contract_Address="",langguage=""):
    """
           合并goPlusResult与symbolResult的字典数据，并进行合理的数据类型转换与默认值处理
       """

    def safe_get(d, key, default=None):
        return d.get(key, default)

    max_supply = safe_get(CMCResult, "max_supply")
    price = safe_get(CMCResult, "quote")
    if not price:
        price = 0.0
    else:
        price = price.get("USD").get("price")

    if max_supply is not None and price is not None:
        fdv = max_supply * price
    else:
        fdv = 0.0  # 或者 None，根据你的业务需求决定

    circulating_supply = safe_get(CMCResult, "circulating_supply")
    mcap = (circulating_supply or 0) * (price or 0)

    max_supply = safe_get(CMCResult, "max_supply")
    if not max_supply:
        max_supply = 0

    circulating_supply = safe_get(CMCResult, "circulating_supply")

    token_symbol = safe_get(goPlusResult, "token_symbol")

    creator_address = safe_get(goPlusResult, "creator_address")
    owner_address = safe_get(goPlusResult, "owner_address")
    holder_count = safe_get(goPlusResult, "holder_count")
    # 设置高精度以确保中间计算准确
    getcontext().prec = 28
    # 计算前十holders信息余额信息
    top10Banlance = sum_top_10_balances(safe_get(goPlusResult, "holders"))
    top10_holders_ratio = sum_top10_holders_ratio(safe_get(goPlusResult, "holders"))


    #下面进行注册器注册
    #注册是否开源的枚举器
    registry = EnumValueRegistry()
    registry.register("is_open_source") \
        .on("1",
            titles={
                LanguageEnum.EN.value:"Contract Source Code Verified",
                LanguageEnum.ZH_HANS.value:"合约已开源",
                LanguageEnum.ZH_HANT.value:"合約已開源",
            },
            descriptions={
                LanguageEnum.EN.value: "This token contract is open source. You can check the contract code for details. Unsourced token contracts are likely to have malicious functions to defraud their users of their assets",
                LanguageEnum.ZH_HANS.value:"此代币合约已开源，可查询合约代码详情。未开源的代币合约更可能存在恶意机制，骗取用户资产。",
                LanguageEnum.ZH_HANT.value:"此代幣合約已開源，可查詢合約代碼詳情。未開源的代幣合約更可能有惡意機制，騙用戶資產"
            },
            riskLevel="Risky",
            risked=False)\
        .on("0",
            titles={
                LanguageEnum.EN.value: "Contract Source Code Can't Verified",
                LanguageEnum.ZH_HANS.value: "合约未开源",
                LanguageEnum.ZH_HANT.value: "合約未開源",
            },
            descriptions={
                LanguageEnum.EN.value: "This token contract is not open source. Unsourced token contracts are likely to have malicious functions to defraud their users of their assets.",
                LanguageEnum.ZH_HANS.value: "此代币合约未开源。未开源的代币合约更可能存在恶意机制，骗取用户资产。",
                LanguageEnum.ZH_HANT.value: "此代幣合約未開源。未開源的代幣合約更可能存在惡意機制，可能騙取用戶資產。"
            },
            riskLevel="Risky",
            risked=True)\
    .register("is_proxy")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "In This Contract, There Is A Proxy Contract.",
            LanguageEnum.ZH_HANS.value: "有代理合约",
            LanguageEnum.ZH_HANT.value: "有代理合約",
        },
        descriptions={
            LanguageEnum.EN.value: "The proxy contract means contract owner can modifiy the function of the token and possibly effect the price.",
            LanguageEnum.ZH_HANS.value: "代理机制是指项目方通过代理合约可能替换此币的相关逻辑，进而对此币价格、机制产生影响",
            LanguageEnum.ZH_HANT.value: "代理機制是指方透過代理合約可能替換此幣的相關邏輯，進而對此幣價格、機制產生影響。"
        },
        riskLevel="Risky",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "No Proxy",
            LanguageEnum.ZH_HANS.value: "无代理合约",
            LanguageEnum.ZH_HANT.value: "無代理合約",
        },
        descriptions={
            LanguageEnum.EN.value: "There is no proxy in the contract. The proxy contract means contract owner can modifiy the function of the token and possibly effect the price.",
            LanguageEnum.ZH_HANS.value: "合约中不包含代理机制。代理机制是指项目方通过代理合约可能替换此币的相关逻辑，进而对此币价格、机制产生影响。",
            LanguageEnum.ZH_HANT.value: "合約中不包含代理機制。代理機制是指項目方通過代理合約可能替換此幣的相關邏輯，進而對此幣價格、機制產生影響。"
        },
        riskLevel="Risky",
        risked=False,
        )\
    .register("is_mintable")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "Mint function",
            LanguageEnum.ZH_HANS.value: "可增发",
            LanguageEnum.ZH_HANT.value: "可增發",
        },
        descriptions={
            LanguageEnum.EN.value: "The contract may contain additional issuance functions, which could maybe generate a large number of tokens, resulting in significant fluctuations in token prices. It is recommended to confirm with the project team whether it complies with the token issuance instructions.",
            LanguageEnum.ZH_HANS.value: "合约疑似保留了增发功能，可能会生成大量代币，造成代币价格大幅波动。建议先与项目方确认是否符合代币发行说明",
            LanguageEnum.ZH_HANT.value: "合約疑似保留了增發功能，可能會生成大量代幣，造成代幣價格大幅波動。建議先與項目方確認是否符合代幣發行說明。"
        },
        riskLevel="Attention",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "No Mint Function",
            LanguageEnum.ZH_HANS.value: "未发现增发功能",
            LanguageEnum.ZH_HANT.value: "未發現增發功能",
        },
        descriptions={
            LanguageEnum.EN.value: "Mint function is transparent or non-existent. Hidden mint functions may increase the amount of tokens in circulation and effect the price of the token.",
            LanguageEnum.ZH_HANS.value: "此代币不存在不明增发机制。不明增发机制可能会增加市面上的该币数量，影响此币价格。",
            LanguageEnum.ZH_HANT.value: "未發現代幣合約存在自毀功能。若存在該功能並被觸發，合約將會銷毀，所有功能不可用，相關資產也會被清除。"
        },
        riskLevel="Attention",
        risked=False)\
    .register("can_take_back_ownership")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "Function Has Been Found That Can Revoke Ownership",
            LanguageEnum.ZH_HANS.value: "可取回所有权",
            LanguageEnum.ZH_HANT.value: "可取回所有權",
        },
        descriptions={
            LanguageEnum.EN.value: "If this function exists, it is possible for the project owner to regain ownership even after relinquishing it",
            LanguageEnum.ZH_HANS.value: "若存在取回所有权的逻辑，可能让项目方在放弃所有权后重新获取owner权限",
            LanguageEnum.ZH_HANT.value: "若存在取回所有權的邏輯，可能讓項目方在放棄所有權後重新獲取 Owner 權限。"
        },
        riskLevel="Attention",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "No Function Found That Retrieves Ownership",
            LanguageEnum.ZH_HANS.value: "未发现可取回所有权",
            LanguageEnum.ZH_HANT.value: "未發現可取回所有權",
        },
        descriptions={
            LanguageEnum.EN.value: "If this function exists, it is possible for the project owner to regain ownership even after relinquishing it",
            LanguageEnum.ZH_HANS.value: "若存在取回所有权的逻辑，可能让项目方在放弃所有权后重新获取owner权限。",
            LanguageEnum.ZH_HANT.value: "若存在取回所有權的邏輯，可能讓項目方在放棄所有權後重新獲取 Owner 權限。"
        },
        riskLevel="Attention",
        risked=False)\
    .register("owner_change_balance")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "Owner Can Change Balance",
            LanguageEnum.ZH_HANS.value: "Owner可修改余额",
            LanguageEnum.ZH_HANT.value: "Owner 可修改餘額",
        },
        descriptions={
            LanguageEnum.EN.value: "The contract owner is found to have the authority to modify the token balances of other addresses.",
            LanguageEnum.ZH_HANS.value: "合同owner有权修改其他地址的代币余额，这可能导致用户资产损失",
            LanguageEnum.ZH_HANT.value: "合約 Owner 有權修改其他地址的代幣餘額，這可能導致用戶資產損失。"
        },
        riskLevel="Risky",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "Owner Can't Change Balance",
            LanguageEnum.ZH_HANS.value: "未发现Owner可改余额",
            LanguageEnum.ZH_HANT.value: "未發現 Owner 可修改餘額",
        },
        descriptions={
            LanguageEnum.EN.value: "The contract owner is not found to have the authority to modify the balance of tokens at other addresses.",
            LanguageEnum.ZH_HANS.value: "未发现合约owner有权修改其他地址的代币余额。",
            LanguageEnum.ZH_HANT.value: "未發現合約 Owner 有權修改其他地址的代幣餘額。"
        },
        riskLevel="Risky",
        risked=False)\
    .register("hidden_owner")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "Hidden Ownership Detected",
            LanguageEnum.ZH_HANS.value: "发现隐藏的owner",
            LanguageEnum.ZH_HANT.value: "發現隱藏的 Owner",
        },
        descriptions={
            LanguageEnum.EN.value: "Hidden owner address was found for the token. For contracts with hidden owner, developer can still manipulate the contract even if the ownership has been abandoned",
            LanguageEnum.ZH_HANS.value: "发现了代币的隐藏owner地址。对于隐藏所有者的合约，即使所有权已被放弃，开发者仍然可以操纵合约",
            LanguageEnum.ZH_HANT.value: "發現了代幣的隱藏 Owner 地址。對於隱藏所有者的合約，即使所有權已被放棄，開發者仍然可以操縱合約。"
        },
        riskLevel="Attention",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "No Hidden Owner",
            LanguageEnum.ZH_HANS.value: "未发现隐藏的owner",
            LanguageEnum.ZH_HANT.value: "未發現隱藏的 Owner",
        },
        descriptions={
            LanguageEnum.EN.value: "No hidden owner address was found for the token. For contract with a hidden owner, developer can still manipulate the contract even if the ownership has been abandoned.",
            LanguageEnum.ZH_HANS.value: "未发现该代币存在隐藏的owner地址。若存在隐藏owner，代币可能会名义上放弃所有权，实际上依然提供存在隐藏的owner控制代币。",
            LanguageEnum.ZH_HANT.value: "未發現該代幣存在隱藏的 Owner 地址。若存在隱藏 Owner，代幣可能會名義上放棄所有權，實際上依然提供存在隱藏的 Owner 控制代幣。"
        },
        riskLevel="Attention",
        risked=False)\
    .register("selfdestruct")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "This Token Can  Self Destruct",
            LanguageEnum.ZH_HANS.value: "该代币能自毁",
            LanguageEnum.ZH_HANT.value: "該代幣能自毀",
        },
        descriptions={
            LanguageEnum.EN.value: "Self-destruct function found. If triggered, the contract will be destroyed, all functions will become unavailable, and all related assets will be erased",
            LanguageEnum.ZH_HANS.value: "发现自毁功能。一旦触发，合约将被销毁，所有功能将不可用，所有相关资产也将被清除。",
            LanguageEnum.ZH_HANT.value: "發現自毀功能。一旦觸發，合約將被銷毀，所有功能將不可用，所有相關資產也將被清除。"
        },
        riskLevel="Risky",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "This Token Can Not Self Destruct",
            LanguageEnum.ZH_HANS.value: "该代币不能自毁",
            LanguageEnum.ZH_HANT.value: "該代幣不能自毀",
        },
        descriptions={
            LanguageEnum.EN.value: "No self-destruct function found. If this function exists and is triggered, the contract will be destroyed, all functions will be unavailable, and all related assets will be erased.",
            LanguageEnum.ZH_HANS.value: "未发现代币合约存在自毁功能。若存在该功能并被触发，合约将会销毁，所有功能不可用，相关资产也会被清除",
            LanguageEnum.ZH_HANT.value: "未發現代幣合約存在自毀功能。若存在該功能並被觸發，合約將會銷毀，所有功能不可用，相關資產也會被清除。"
        },
        riskLevel="Risky",
        risked=False)\
    .register("external_call")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "External Call Risk Found",
            LanguageEnum.ZH_HANS.value: "存在外部合约调用风险",
            LanguageEnum.ZH_HANT.value: "存在外部合約調用風險",
        },
        descriptions={
            LanguageEnum.EN.value: "External calls would cause this token contract to be highly dependent on other contracts, which may be a potential risk.",
            LanguageEnum.ZH_HANS.value: "当合约执行时会调用外部合约。这将导致该合约高度依赖其他合约，这可能是一个潜在的风险",
            LanguageEnum.ZH_HANT.value: "當合約執行時會調用外部合約。這將導致該合約高度依賴其他合約，這可能是一個潛在的風險。"
        },
        riskLevel="Attention",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "No External Call Risk found",
            LanguageEnum.ZH_HANS.value: "未发现外部合约调用风险",
            LanguageEnum.ZH_HANT.value: "未發現外部合約調用風險",
        },
        descriptions={
            LanguageEnum.EN.value: "External calls would cause this token contract to be highly dependent on other contracts, which may be a potential risk.",
            LanguageEnum.ZH_HANS.value: "外部合约调用将导致代币合约高度依赖其他合约，这可能是一个潜在的风险。",
            LanguageEnum.ZH_HANT.value: "外部合約調用將導致代幣合約高度依賴其他合約，這可能是一個潛在的風險。"
        },
        riskLevel="Attention",
        risked=False)\
    .register("gas_abuse")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "This token is a gas abuser",
            LanguageEnum.ZH_HANS.value: "发现gas滥用",
            LanguageEnum.ZH_HANT.value: "發現 Gas 濫用",
        },
        descriptions={
            LanguageEnum.EN.value: "Gas abuse activity has been found.",
            LanguageEnum.ZH_HANS.value: "发现了滥用gas的活动。",
            LanguageEnum.ZH_HANT.value: "發現了濫用 Gas 的活動。"
        },
        riskLevel="Attention",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "This Token Is Not A Gas Abuser",
            LanguageEnum.ZH_HANS.value: "未发现gas滥用",
            LanguageEnum.ZH_HANT.value: "未發現 Gas 濫用",
        },
        descriptions={
            LanguageEnum.EN.value: "No gas abuse activity has been found.",
            LanguageEnum.ZH_HANS.value: "没有证据表明该合约存在gas滥用行为",
            LanguageEnum.ZH_HANT.value: "沒有證據表明該合約存在 Gas 濫用行為。"
        },
        riskLevel="Attention",
        risked=False)\
    .on("",
        titles={
            LanguageEnum.EN.value: "This Token Is Not A Gas Abuser",
            LanguageEnum.ZH_HANS.value: "未发现gas滥用",
            LanguageEnum.ZH_HANT.value: "未發現 Gas 濫用",
        },
        descriptions={
            LanguageEnum.EN.value: "No gas abuse activity has been found.",
            LanguageEnum.ZH_HANS.value: "没有证据表明该合约存在gas滥用行为",
            LanguageEnum.ZH_HANT.value: "沒有證據表明該合約存在 Gas 濫用行為。"
        },
        riskLevel="Attention",
        risked=False)\
    .register("is_honeypot")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "This Appears To Be A Honeypot",
            LanguageEnum.ZH_HANS.value: "可能是貔貅代币",
            LanguageEnum.ZH_HANT.value: "可能是貔貅代幣。",
        },
        descriptions={
            LanguageEnum.EN.value: "We are aware of malicious code.",
            LanguageEnum.ZH_HANS.value: "发现恶意代码",
            LanguageEnum.ZH_HANT.value: "發現惡意代碼"
        },
        riskLevel="Risky",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "This Does Not Appear To Be A Honeypot",
            LanguageEnum.ZH_HANS.value: "可能不是貔貅代币",
            LanguageEnum.ZH_HANT.value: "可能不是貔貅代幣",
        },
        descriptions={
            LanguageEnum.EN.value: "We are not aware of any malicious code.",
            LanguageEnum.ZH_HANS.value: "暂未发现该代币包含恶意代码。",
            LanguageEnum.ZH_HANT.value: "沒有證據表明該合約存在 Gas 濫用行為。"
        },
        riskLevel="Risky",
        risked=False)\
    .register("transfer_pausable")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "Functions That Can Suspend Trading",
            LanguageEnum.ZH_HANS.value: "可暂停交易",
            LanguageEnum.ZH_HANT.value: "可暫停交易",
        },
        descriptions={
            LanguageEnum.EN.value: "If a suspendable code is included, the token maybe neither be bought nor sold (honeypot risk)",
            LanguageEnum.ZH_HANS.value: "合约存在可暂停交易的逻辑，可能导致该代币的买卖交易全部暂停（貔貅风险）。",
            LanguageEnum.ZH_HANT.value: "合約存在可暫停交易的邏輯，可能導致該代幣的買賣交易全部暫停（貔貅風險）。"
        },
        riskLevel="Attention",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "NO Codes Found To Suspend Trading",
            LanguageEnum.ZH_HANS.value: "无暂停交易功能",
            LanguageEnum.ZH_HANT.value: "無暫停交易功能",
        },
        descriptions={
            LanguageEnum.EN.value: "If a suspendable code is included, the token maybe neither be bought nor sold (honeypot risk).",
            LanguageEnum.ZH_HANS.value: "若存在暂停交易功能，可能导致该代币的买卖交易全部暂停（貔貅风险）。",
            LanguageEnum.ZH_HANT.value: "若存在暫停交易功能，可能導致該代幣的買賣交易全部暫停（貔貅風險）。"
        },
        riskLevel="Attention",
        risked=False)\
    .register("trading_cooldown")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "Trading Cooldown Function Exists",
            LanguageEnum.ZH_HANS.value: "存在交易冷却功能",
            LanguageEnum.ZH_HANT.value: "存在交易冷卻功能",
        },
        descriptions={
            LanguageEnum.EN.value: "The token contract has  trading cooldown function. If there is a trading cooldown function, the user will not be able to sell the token within a certain time or block after buying.",
            LanguageEnum.ZH_HANS.value: "代币合约有交易冷却功能，若有交易冷却功能，则用户买入代币后，在一定时间或区块内将无法卖出。",
            LanguageEnum.ZH_HANT.value: "代幣合約有交易冷卻功能，若有交易冷卻功能，則用戶買入代幣後，在一定時間或區塊內將無法賣出。"
        },
        riskLevel="Attention",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "No Trading Cooldown Function",
            LanguageEnum.ZH_HANS.value: "无交易冷却功能",
            LanguageEnum.ZH_HANT.value: "無交易冷卻功能",
        },
        descriptions={
            LanguageEnum.EN.value: "The token contract has no trading cooldown function. If there is a trading cooldown function, the user will not be able to sell the token within a certain time or block after buying.",
            LanguageEnum.ZH_HANS.value: "该代币合约无交易冷却功能。若有交易冷却功能，用户在购买后的一定时间或区块内将不能出售代币。",
            LanguageEnum.ZH_HANT.value: "該代幣合約無交易冷卻功能。若有交易冷卻功能，用戶在購買後的一定時間或區塊內將不能出售代幣。"
        },
        riskLevel="Attention",
        risked=False)\
    .register("is_anti_whale")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "Anti-Whale Mechanism Exists (Limited Number Of Transactions)",
            LanguageEnum.ZH_HANS.value: "防巨鲸（限制交易数量）",
            LanguageEnum.ZH_HANT.value: "防巨鯨（限制交易數量）",
        },
        descriptions={
            LanguageEnum.EN.value: "There is a limit to the number of token transactions. The number of scam token transactions may be limited (honeypot risk).",
            LanguageEnum.ZH_HANS.value: "此代币卖出数量受到限制。很多项目的代币会限制买卖的数量，从而导致用户无法顺利变现。",
            LanguageEnum.ZH_HANT.value: "此代幣賣出數量受到限制。很多項目的代幣會限制買賣的數量，從而導致用戶無法順利變現。"
        },
        riskLevel="Attention",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "No Anti_Whale(Unlimited Number Of Transactions)",
            LanguageEnum.ZH_HANS.value: "交易数量不限",
            LanguageEnum.ZH_HANT.value: "交易數量不限",
        },
        descriptions={
            LanguageEnum.EN.value: "There is no limit to the number of token transactions. The number of scam token transactions may be limited (honeypot risk).",
            LanguageEnum.ZH_HANS.value: "代币的交易数量不受限制。很多诈骗项目的代币可能会限制买卖的数量。",
            LanguageEnum.ZH_HANT.value: "代幣的交易數量不受限制。許多詐騙項目的代幣可能會限制買賣的數量。"
        },
        riskLevel="Attention",
        risked=False)\
    .register("anti_whale_modifiable")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "Anti Whale Can  Be Modified",
            LanguageEnum.ZH_HANS.value: "防巨鲸可改",
            LanguageEnum.ZH_HANT.value: "防巨鯨可改",
        },
        descriptions={
            LanguageEnum.EN.value: "The maximum trading amount or maximum position can  be modified.",
            LanguageEnum.ZH_HANS.value: "交易最大额度或最大持仓量可被修改，这有可能导致交易暂停",
            LanguageEnum.ZH_HANT.value: "交易最大額度或最大持倉量可被修改，這有可能導致交易暫停。"
        },
        riskLevel="Attention",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "Anti Whale Can Not Be modified",
            LanguageEnum.ZH_HANS.value: "防巨鲸不可改",
            LanguageEnum.ZH_HANT.value: "防巨鯨不可更改",
        },
        descriptions={
            LanguageEnum.EN.value: "The maximum trading amount or maximum position can not be modified",
            LanguageEnum.ZH_HANS.value: "交易最大额度或最大持仓量不可被修改。",
            LanguageEnum.ZH_HANT.value: "交易最大額度或最大持倉量不可被修改。"
        },
        riskLevel="Attention",
        risked=False)\
    .register("is_blacklisted")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "Blacklist Function",
            LanguageEnum.ZH_HANS.value: "可设置黑名单",
            LanguageEnum.ZH_HANT.value: "可設置黑名單",
        },
        descriptions={
            LanguageEnum.EN.value: "The blacklist function is included. Some addresses may not be able to trade normally (honeypot risk).",
            LanguageEnum.ZH_HANS.value: "交易最大额度或最大持仓量不可被修改。",
            LanguageEnum.ZH_HANT.value: "交易最大額度或最大持倉量不可被修改。"
        },
        riskLevel="Risky",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "NO Blacklist",
            LanguageEnum.ZH_HANS.value: "不包含黑名单",
            LanguageEnum.ZH_HANT.value: "不包含黑名單",
        },
        descriptions={
            LanguageEnum.EN.value: "The blacklist function is not included. If there is a blacklist, some addresses may not be able to trade normally (honeypot risk).",
            LanguageEnum.ZH_HANS.value: "此合约中不包含黑名单机制，若存在黑名单，可能会有部分用户被限制交易（貔貅风险）。",
            LanguageEnum.ZH_HANT.value: "此合約中不包含黑名單機制，若存在黑名單，可能會導致部分用戶被限制交易（貔貅風"
        },
        riskLevel="Risky",
        risked=False)\
    .register("is_whitelisted")\
    .on("1",
        titles={
            LanguageEnum.EN.value: "Whitelist Function",
            LanguageEnum.ZH_HANS.value: "可设置白名单",
            LanguageEnum.ZH_HANT.value: "可設置白名單",
        },
        descriptions={
            LanguageEnum.EN.value: "Having a whitelist function means that, for this contract, some privileged users may have greater advantages in transactions, such as bypassing transaction limits, being exempt from taxes, trading earlier than others, or not being affected by transaction cooldown restrictions.",
            LanguageEnum.ZH_HANS.value: "对于本合约来说，拥有白名单功能意味着对一些特权用户可能在交易中拥有更大的优势，比如绕过交易限制、免税、比其他人更早交易、或者不受交易冷却时间限制的影响。",
            LanguageEnum.ZH_HANT.value: "對於本合約來說，擁有白名單功能意味著對一些特權用戶可能在交易中擁有更大的優勢，比如繞過交易限制、免稅、比其他人更早交易、或者不受交易冷卻時間限制的影響。"
        },
        riskLevel="Risky",
        risked=True)\
    .on("0",
        titles={
            LanguageEnum.EN.value: "No Whitelist",
            LanguageEnum.ZH_HANS.value: "不包含白名单机制",
            LanguageEnum.ZH_HANT.value: "不包含白名單機制",
        },
        descriptions={
            LanguageEnum.EN.value: "The whitelist function is not included. If there is a whitelist, some addresses may not be able to trade normally (honeypot risk).",
            LanguageEnum.ZH_HANS.value: "合约中不包含白名单机制。若存在白名单，那么会有一部分地址可能无法正常交易（貔貅风险）。",
            LanguageEnum.ZH_HANT.value: "合約中不包含白名單機制。若存在白名單，那麼會有一部分地址可能無法正常交易（貔貅風險）。"
        },
        riskLevel="Risky",
        risked=False)







    is_open_source = safe_get(goPlusResult,"is_open_source")
    is_proxy=safe_get(goPlusResult,"is_proxy")
    is_mintable= safe_get(goPlusResult,"is_mintable")
    can_take_back_ownership=safe_get(goPlusResult,"can_take_back_ownership")
    owner_change_balance=safe_get(goPlusResult,"owner_change_balance")
    hidden_owner=safe_get(goPlusResult,"hidden_owner")
    selfdestruct=safe_get(goPlusResult,"selfdestruct")
    external_call=safe_get(goPlusResult,"external_call")
    gs_tooken = safe_get(goPlusResult,"gas_abuse")
    gs_tooken = str(gs_tooken).strip() or "0"
    buy_tax=safe_get(goPlusResult, "buy_tax")
    sell_tax=safe_get(goPlusResult,"sell_tax")
    is_honeypot=safe_get(goPlusResult,"is_honeypot")
    transfer_pausable=safe_get(goPlusResult,"transfer_pausable")
    trading_cooldown=safe_get(goPlusResult,"trading_cooldown")
    is_anti_whale=safe_get(goPlusResult,"is_anti_whale")
    anti_whale_modifiable=safe_get(goPlusResult,"anti_whale_modifiable")
    tax_Cannot_Be_Modified = ""
    is_blacklisted=safe_get(goPlusResult,"is_blacklisted")
    is_whitelisted= safe_get(goPlusResult,"is_whitelisted")
    personal_Addresses=""

    Dex_And_Liquidity=safe_get(goPlusResult,"dex")
    Social_Media=[{}] #暂时是空的
    # 引入格式化TokenPrice 进行展示的人物
    from app.utuls.format_price_display import format_price_display
    calute_price = format_price_display(price)
    #基础信息
    deep_research_report_basic = {
        "Token_Price": calute_price,
        "FDV": format_number(fdv),
        "M.Cap": format_number(mcap),
        "Max_Supply": format_number(max_supply),
        "Circulation": format_number(circulating_supply),
        "Token_Symbol": token_symbol,
        "Contract_Address": Contract_Address,  # 按照前四后六进行展示
        "Contract_Creator": creator_address,  # 按照前四后六进行展示
        "Contract_Owner": owner_address,  # 按照前四后六进行展示
        "Toker_Holders": holder_count,  # 统计风险项和注意项的总数。
        "Token_Supply": format_number(float(top10Banlance)),  # 保留小数点后两位展示。直接展示真实数字，不需要进行k m b单位换算。
        "Top10_Holders_Ratio": str(top10_holders_ratio * 100) + "%",  # 保留小数点后两位并采用百分比展示。
        "AttentionItem":0,#注意事项
        "RiskyItem":0,#风险事项
    }
    deep_contract_security_array,risk_count=  count_risks_filtered([
        registry.format("is_open_source", is_open_source,language=langguage),
        registry.format("is_proxy", is_proxy,language=langguage),
        registry.format("is_mintable", is_mintable,language=langguage),
        registry.format("can_take_back_ownership", can_take_back_ownership,language=langguage),
        registry.format("hidden_owner", hidden_owner,language=langguage),
        registry.format("selfdestruct", selfdestruct,language=langguage),
        registry.format("external_call", external_call,language=langguage),
        registry.format("gas_abuse", gs_tooken,language=langguage)],risk_level="Risky")

    _, attention_count = count_risks_filtered([
        registry.format("is_open_source", is_open_source,language=langguage),
        registry.format("is_proxy", is_proxy,language=langguage),
        registry.format("is_mintable", is_mintable,language=langguage),
        registry.format("can_take_back_ownership", can_take_back_ownership,language=langguage),
        registry.format("hidden_owner", hidden_owner,language=langguage),
        registry.format("selfdestruct", selfdestruct,language=langguage),
        registry.format("external_call", external_call,language=langguage),
        registry.format("gas_abuse", gs_tooken,language=langguage)], risk_level="Attention")

    list_array,risk_count_hot=count_risks_filtered([
           registry.format("is_honeypot", is_honeypot,language=langguage),
           registry.format("transfer_pausable", transfer_pausable,language=langguage),
           registry.format("trading_cooldown", trading_cooldown,language=langguage),
           registry.format("is_anti_whale", is_anti_whale,language=langguage),
           registry.format("anti_whale_modifiable", anti_whale_modifiable,language=langguage),
           registry.format("is_blacklisted", is_blacklisted,language=langguage),
           registry.format("is_whitelisted", is_whitelisted,language=langguage),
        ],risk_level="Risky")

    _,attention_count_hot = count_risks_filtered([
        registry.format("is_honeypot", is_honeypot,language=langguage),
        registry.format("transfer_pausable", transfer_pausable,language=langguage),
        registry.format("trading_cooldown", trading_cooldown,language=langguage),
        registry.format("is_anti_whale", is_anti_whale,language=langguage),
        registry.format("anti_whale_modifiable", anti_whale_modifiable,language=langguage),
        registry.format("is_blacklisted", is_blacklisted,language=langguage),
        registry.format("is_whitelisted", is_whitelisted,language=langguage),
    ], risk_level="Attention")
    deep_honeypot_risk = {
        "Buy_Tax": format_percentage(buy_tax, decimals=2),
        "Sell_Tax": format_percentage(sell_tax, decimals=2),
        "description":"Above 10% may be considered a high tax rate. More than 50% tax rate means may not be tradable.",
        "list": list_array
    }
    if langguage==LanguageEnum.ZH_HANS.value:
        deep_honeypot_risk.update({"description":"税率若超过10%就算偏高；若超过50%可能会导致无法交易。"})
    if langguage==LanguageEnum.ZH_HANT.value:
        deep_honeypot_risk.update({"description":"稅率若超過 10% 就算偏高；若超過 50% 可能會導致無法交易。"})

    deep_research_report_basic.update({"RiskyItem":risk_count+risk_count_hot})
    deep_research_report_basic.update({"AttentionItem":attention_count+attention_count_hot})
    detail_info = {
        "basic_info":deep_research_report_basic,#基础信息
        "contract_security":deep_contract_security_array,#安全信息
        "honeypot_risk":deep_honeypot_risk,#其他风险信息
        "Dex_And_Liquidity":Dex_And_Liquidity#其他信息
    }
    # 组织返回基础信息
    return format_and_convert_keys(detail_info)

#其他类型API工具分析
def api_extra_asnyc(selectedType,type_value,langguage):
    chain_id = selectedType.get("chain_id")

    # 检查 chain_id 是否为字符串，并且不是数字
    if isinstance(chain_id, str) and not chain_id.isdigit():
        chain_id = 56  # 默认为 56
    else:
        # 如果是数字字符串或其他类型，转换为整数
        chain_id = int(chain_id) if chain_id else 56

    contract_addresses = selectedType.get("contract_addresses")
    symbol= selectedType.get("symbol")
    response = {"overview":{},"details":{}}
    print("selectedType:")
    print(selectedType)
    #goPlusResult
    goPlusResult = GoPlusAPISearch(chain_id, contract_addresses)
    #symbolResult
    symbolResult = SymbolAPISearch(symbol)

    print("symbolResult:==============", symbolResult)
    print("goPlusResult:=============", goPlusResult)
    if goPlusResult and symbolResult :
        symbolResult = symbolResult[0]  # 只取第一个数组数据
        response["overview"] = uniongoPlusResultAndsymbolResultOverView(goPlusResult, symbolResult, contract_addresses,langguage)
        response["details"] = uniongoPlusResultAndsymbolResultDetails(goPlusResult, symbolResult, contract_addresses,langguage)

    response["type"] = type_value
    response["state"] =  TaskState.RESEARCH_TASK_DISPLAY_RESEARCH
    return response

#默认返回处理函数
def default_deal_with(selectedType,type_value,langguage):
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
        "state": TaskState.RESEARCH_TASK_DISPLAY_PROMPTED_PROJECT,
        "type":"",
    }

# 将 snake_case 转换为 camelCase
def to_camel_case(snake_str: str) -> str:
    components = snake_str.split('_')
    return components[0].lower() + ''.join(x.title() for x in components[1:])

# 将字典中的键名从 snake_case 转为 camelCase 并过滤空值
def format_and_convert_keys(data: dict) -> dict:
    filtered = filter_empty_values(data)
    return {to_camel_case(k): v for k, v in filtered.items()}


#新增类型处理
def wrap_del_with_OverView(detail_data,langguage):
    #默认初始化为项目信息
    price = detail_data.get("price", "")
    if not price:
        price = 0.0

    fdv = detail_data.get("fully_diluted_market_cap", "")
    if not fdv:
        fdv=0

    MCap=detail_data.get("market_cap", "")
    if not MCap:
        MCap=0

    total_funding=detail_data.get("total_funding", "")
    if not total_funding:
        total_funding=0

    followers=detail_data.get("followers", "")
    if not  followers:
        followers=0

    from app.utuls.format_price_display import format_price_display_project
    print(price)
    calute_price = format_price_display_project(float(price))
    res = format_and_convert_keys({
        "Project_Name": detail_data.get("project_name", ""),
        "logo": detail_data.get("logo", ""),
        "Token_Symbol": detail_data.get("token_symbol", ""),
        "Token_Price": calute_price,
        "FDV": format_number(fdv),
        "M.Cap": format_number(MCap),
        "Brief": detail_data.get("one_liner", ""),
        "Fundraising_Amount": format_number(total_funding),
        "Ecosystem": detail_data.get("ecosystem", ""),
        "X_Followers":format_number(followers),
        "Description": detail_data.get("description")
    })
    #如果不是项目如果是4 VCTOKEN主流币
#     if type==4:
#         res = {
#     "Token_Price": detail_data.get("price", ""),
#     "logo": detail_data.get("logo", ""),
#     "Token_Symbol": detail_data.get("token_symbol", ""),
#     "Project_Name": detail_data.get("project_name", ""),
#     "FDV": detail_data.get("fully_diluted_market_cap", ""),
#     "M.Cap": detail_data.get("market_cap", ""),
#     "Brief": detail_data.get("one_liner", ""),
#     "Fundraising_Amount": detail_data.get("total_funding", ""),
#     "Ecosystem": detail_data.get("ecosystem", ""),
#     "X_Followers": detail_data.get("followers", "")
# }

    return res



def handle_type_based_data(type_item, attached_data,langguage):
    """
    根据项目类型处理不同逻辑
    """
    #如果为空则默认返回空的结构
    if not  type_item:
        return EmptyResult()
    #如果不为空则进行根据type整合数据
    type_value = type_item.get("type")
    state = TaskState.RESEARCH_TASK_DISPLAY_RESEARCH

    if type_value in [2, 4]:
        # 走 getDetailRowdata 查询
        detail_data = getDetailRowdata(type_item)
        if detail_data:
            return {
                "overview": wrap_del_with_OverView(detail_data,langguage),
                "details": wrap_del_with_detail(detail_data,langguage),
                "state": state,
                "type":type_value
            }

    elif type_value == 3:
        # 调用其他API处理（示例逻辑）
        # 你可以定义自己的函数 fetch_type4_data()
        return api_extra_asnyc(type_item,type_value,langguage)
    elif type_value == 1:
        return account_deep_asynic(type_item,type_value,langguage)

    else:
        # 默认：不支持的类型，清空数据结构
        return default_deal_with(type_item,type_value,langguage)


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
        "apikey": "TIvihog4hNGbhNWpuaRUR4NMW0hDfyoZ",
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
        "apikey": "TIvihog4hNGbhNWpuaRUR4NMW0hDfyoZ",
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

#测试分类信息
def call_llm_chain_wrap(state: AgentState):
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


def filter_items(data_list):
    if not data_list or not isinstance(data_list, list):
        return []

    def is_valid_type_2_or_4(item):
        return item.get("type") in (2, 4) and isinstance(item.get("id"), int)

    def is_valid_type_3(item):
        return (
            item.get("type") == 3
            and item.get("chain_id") not in (None, "", [])
            and item.get("contract_addresses")
            and item.get("symbol")
        )

    return [item for item in data_list if is_valid_type_2_or_4(item) or is_valid_type_3(item)]


def add_title_prefix(item_type, title):
    """
    根据 item_type 添加对应的 title 前缀
    """
    if not title:
        return title

    if item_type == 3:
        return f"Analysis report of the {title}"
    elif item_type in [2, 4]:
        return f"Background information of the {title}"
    return title

#需要根据返回的typelist进行优化处理
def wrapListInfo(typelist):
    new_list = []

    for item in typelist:
        item_type = item.get("type")

        if item_type not in [1, 2, 3, 4]:
            continue

        if item_type == 3:
            title = item.get("title", "")
            item = item.copy()
            item["title"] = add_title_prefix(item_type, title)
            new_list.append(item)

        elif item_type in [2, 4]:
            title = item.get("title")
            if not title:
                new_list.append(item)
                continue

            search_result = searchRowData(title).get("data")
            if isinstance(search_result, list) and len(search_result) > 0:
                first_data = search_result[0]
                print("first_data:", first_data)

                updated_item = item.copy()
                updated_item.update({
                    "id": first_data.get("id"),
                    "title": add_title_prefix(item_type, first_data.get("name")),
                    "logo": first_data.get("logo"),
                    "symbol":first_data.get("name"),
                    "detail": first_data.get("introduce")
                })

                new_list.append(updated_item)
            else:
                item = item.copy()
                item["title"] = add_title_prefix(item_type, title)
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
        data["intent"] = Intention.deep_research.value #这里已经进来了为什么还要继承
        timestamp_time = time.time()
        print("使用 time 模块获取的 UTC 时间戳:", timestamp_time)
        data["timestamp"] = state.attached_data.get("timestamp", timestamp_time)
        selectedType = {}
        if state.attached_data:
            form = state.attached_data.get("form")
            if form is not None:
                selectedType = form.get("selectedType", {})
            else:
                selectedType = {}

        handled_result = handle_type_based_data(selectedType, state.attached_data,state.langguage)
        print("handled_result:", handled_result)
        description = data.get("description","")
        #只有在选中的时候进行处理
        if selectedType:
            print("selectedType:=====", selectedType)
            description = "I have confirmed the information to be queried. Kindly assist in retrieving the relevant data."
            if state.langguage == LanguageEnum.ZH_HANS.value:
                description = "我已确认待查询信息。请你协助检索相关数据。"
            if state.langguage == LanguageEnum.ZH_HANT.value:
                description = "我已確認待查詢資訊。請你協助檢索相關數據。"

            if not handled_result.get("details"):
                if state.langguage == LanguageEnum.ZH_HANS.value:
                    description = "报告暂未生成成功"
                if state.langguage == LanguageEnum.ZH_HANT.value:
                    description = "報告尚未生成成功"
                if state.langguage == LanguageEnum.EN.value:
                    description = "Report generation is not complete yet"
        print("data:======")
        print("description:", description)

        data.update({
            "description":description,
            "overview": handled_result.get("overview", {}),
            "details": handled_result.get("details", {}),
            "state": handled_result.get("state", ""),
            "type":handled_result.get("type")
        })
        print("data:", data)
        return state.copy(update={"result": data,"detected_intent":Intention.deep_research.value})

    # 情况一：attached_data 存在
    if state.attached_data:
        selected_type = state.attached_data.get("form").get("selectedType")
        data = state.attached_data if selected_type else None

        if not selected_type:
            print("未选择 selectedType，调用 LLM...")
            response_data = call_llm_chain(state)
            print("deep_search_data")
            data = response_data.get("data", {})
            print("deep_search_data:", data)
            if data.get("missFields"):
                data["intent"] = Intention.deep_research.value
                timestamp_time = time.time()
                data["timestamp"] = state.attached_data.get("timestamp", timestamp_time)
                return state.copy(update={"result": data})

            # 对 LLM 返回的数据进行处理
            data["typeList"] = filter_items(wrapListInfo(data.get("typeList")))
        return update_result_with_handling(data, state)

    # 情况二：attached_data 不存在，同样调用 LLM
    print("attached_data 不存在，调用 LLM...")
    response_data = call_llm_chain(state)
    print("deep_search_data")
    data = response_data.get("data", {})
    print("deep_search_data:",data)
    if data.get("missFields"):
        data["intent"] = Intention.deep_research.value
        timestamp_time = time.time()
        data["timestamp"] = time.time()
        return state.copy(update={"result": data})

    data["typeList"] = filter_items(wrapListInfo(data.get("typeList")))
    return update_result_with_handling(data, state)
if __name__ == '__main__':
    # 示例调用
    # contract_address = "0x123456789abcdef"
    # contract_creator = "creator12345678"
    # contract_owner = "owner12345678"
    #
    # print(format_string(contract_address))
    # print(format_string(contract_creator))
    # print(format_string(contract_owner))
    # buy_tax = 0.1
    # sell_tax = "0.075"
    #
    # result = {
    #     "Buy_Tax": format_percentage(buy_tax),  # 10%
    #     "Sell_Tax": format_percentage(sell_tax)  # 8%
    # }
    #

    detail_data = {
        "project_name": "AI Launchpad",
        "logo": "",
        "token_symbol": "AILP",
        "one_liner": "Accelerating AI startups",
        "ecosystem": "Ethereum",
        "description": None
    }

    price = 0.1234
    fdv = 5000000
    MCap = 3000000
    total_funding = 1000000
    followers = 15400

    raw_data = {
        "Project_Name": detail_data.get("project_name", ""),
        "logo": detail_data.get("logo", ""),
        "Token_Symbol": detail_data.get("token_symbol", ""),
        "Token_Price": str(round(price, 2)),
        "FDV": fdv,
        "M.Cap": MCap,
        "Brief": detail_data.get("one_liner", ""),
        "Fundraising_Amount": total_funding,
        "Ecosystem": detail_data.get("ecosystem", ""),
        "X_Followers": followers,
        "Description": detail_data.get("description")
    }

    # 应用过滤 + 字段名驼峰转换
    final_data = format_and_convert_keys(raw_data)

    # 输出
    print(final_data)
    # print(result)

