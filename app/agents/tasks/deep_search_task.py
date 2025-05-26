#深度搜索分析
import asyncio
import time
from decimal import Decimal, getcontext

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.form.form import TaskState
from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.overview_asnsy_propmt import OVERVIEW_ASNYC_PROPMT
from app.agents.schemas import AgentState, Intention
from app.agents.tools import send_post_request, send_get_request
from app.agents.lib.redisManger.redisManager import redis_dict_manager
from app.test.deepSearchProject.deepSearchTask_prompt_test import DEEPSEARCHTASK_PROMPT_TEST
from app.agents.tasks.deep_search_task_enum import EnumValueRegistry

#获取rawData数据s
#根据详情信息返回OverView数据
def wrap_del_with_detail(detail_data):
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

    return format_and_convert_keys({
        "Project_Name": detail_data.get("project_name", ""),
        "logo": detail_data.get("logo", ""),
        "Token_Symbol": detail_data.get("token_symbol", ""),
        "Token_Price": str(round(price, 2)),
        "FDV": format_number(fdv),
        "M.Cap": format_number(MCap),
        "Brief": detail_data.get("one_liner", ""),
        "Fundraising_Amount": format_number(total_funding),
        "Ecosystem": detail_data.get("ecosystem", ""),
        "X_Followers": format_number(followers),
        "Description": detail_data.get("description"),
        "Reports":detail_data.get("reports",[]),
        "Events":detail_data.get("event",[]),
        "investors":detail_data.get("investors",[]),
        "Team_Member":detail_data.get("team_members",[]),
        "Social_Media":detail_data.get("social_media",[])
    })

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
        result = res.get("result")
        print("goplusrusult:===", result)
        contract_address = contract_addresses[0]
        print("contract_address:===", contract_address)
        print("type(goplusrusult):===", type(result))
        #0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE
        print("你请求的地址（小写）:", contract_address.lower())
        response = result.get(contract_address.lower())
        print("response:===", response)
        return response
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
    if num < 1000:
        return f"{num:.2f}"
    elif 1000 <= num < 1000000:
        return f"{round(num / 1000, 2):.2f}K"
    elif 1000000 <= num < 1000000000:
        return f"{round(num / 1000000, 2):.2f}M"
    else:
        return f"{round(num / 1000000000, 2):.2f}B"

def format_string(s):
    if len(s) <= 10:
        return s
    return s[:4] + '***' + s[-6:]

def filter_empty_values(info_dict):
    for key, value in info_dict.items():
        if value is None or (isinstance(value, str) and value.strip() == ""):
            info_dict[key] = "--"
    return info_dict

def uniongoPlusResultAndsymbolResultOverView(goPlusResult, CMCResult,Contract_Address=""):
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
    #展示价格方式
    basic_info = {
         "Token_Price": calute_price,
         "FDV": format_number(fdv),
         "M.Cap": format_number(mcap),
         "Max_Supply": format_number(max_supply),
         "Circulation": format_number(circulating_supply),
        "Token_Symbol":token_symbol,
        "Contract_Address":format_string(Contract_Address),#按照前四后六进行展示
        "Contract_Creator":format_string(creator_address),#按照前四后六进行展示
        "Contract_Owner":format_string(owner_address),#按照前四后六进行展示
        "Toker_Holders":holder_count,#统计风险项和注意项的总数。
        "Token_Supply": str(top10Banlance),#保留小数点后两位展示。直接展示真实数字，不需要进行k m b单位换算。
        "Top10_Holders_Ratio": str(top10_holders_ratio*100)+"%",#保留小数点后两位并采用百分比展示。
    }
    #组织返回基础信息
    return format_and_convert_keys(basic_info)

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
def uniongoPlusResultAndsymbolResultDetails(goPlusResult, CMCResult,Contract_Address=""):
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
        .on("1", title="Contract source code verified",
            description="This token contract is open source. You can check the contract code for details. Unsourced token contracts are likely to have malicious functions to defraud their users of their assets") \
        .on("0", title="Contract source code can't verified",
            description="This token contract is not open source. Unsourced token contracts are likely to have malicious functions to defraud their users of their assets.")\
    .register("is_proxy")\
    .on("1",title="In this contract, there is a proxy contract.",description="The proxy contract means contract owner can modifiy the function of the token and possibly effect the price.")\
    .on("0",title="No proxy",description="There is no proxy in the contract. The proxy contract means contract owner can modifiy the function of the token and possibly effect the price.")\
    .register("is_mintable")\
    .on("1",title="Mint function",description="The contract may contain additional issuance functions, which could maybe generate a large number of tokens, resulting in significant fluctuations in token prices. It is recommended to confirm with the project team whether it complies with the token issuance instructions.")\
    .on("0",title="No mint function",description="Mint function is transparent or non-existent. Hidden mint functions may increase the amount of tokens in circulation and effect the price of the token.")\
    .register("can_take_back_ownership")\
    .on("1",title="Function has been found that can revoke ownership",description="If this function exists, it is possible for the project owner to regain ownership even after relinquishing it")\
    .on("0",title="No function found that retrieves ownership",description="If this function exists, it is possible for the project owner to regain ownership even after relinquishing it")\
    .register("owner_change_balance")\
    .on("1",title="Owner can change balance",description="The contract owner is found to have the authority to modify the token balances of other addresses.")\
    .on("0",title="Owner can't change balance",description="The contract owner is not found to have the authority to modify the balance of tokens at other addresses.")\
    .register("hidden_owner")\
    .on("1",title="Hidden ownership detected",description="Hidden owner address was found for the token. For contracts with hidden owner, developer can still manipulate the contract even if the ownership has been abandoned")\
    .on("0",title="No hidden owner",description="No hidden owner address was found for the token. For contract with a hidden owner, developer can still manipulate the contract even if the ownership has been abandoned.")\
    .register("selfdestruct")\
    .on("1",title="This token can  self destruct",description="Self-destruct function found. If triggered, the contract will be destroyed, all functions will become unavailable, and all related assets will be erased.")\
    .on("0",title="This token can not self destruct",description="No self-destruct function found. If this function exists and is triggered, the contract will be destroyed, all functions will be unavailable, and all related assets will be erased.")\
    .register("external_call")\
    .on("1",title="External call risk found",description="External calls would cause this token contract to be highly dependent on other contracts, which may be a potential risk.")\
    .on("0",title="No external call risk found",description="External calls would cause this token contract to be highly dependent on other contracts, which may be a potential risk.")\
    .register("gas_abuse")\
    .on("1",title="This token is a gas abuser",description="Gas abuse activity has been found.")\
    .on("0",title="This token is not a gas abuser",description="No gas abuse activity has been found.")\
    .on("",title="This token is not a gas abuser",description="No gas abuse activity has been found.")\
    .register("is_honeypot")\
    .on("1",title="This appears to be a honeypot",description="We are aware of malicious code.")\
    .on("0",title="This does not appear to be a honeypot",description="We are not aware of any malicious code.")\
    .register("transfer_pausable")\
    .on("1",title="Functions that can suspend trading",description="If a suspendable code is included, the token maybe neither be bought nor sold (honeypot risk).")\
    .on("0",title="No codes found to suspend trading",description="If a suspendable code is included, the token maybe neither be bought nor sold (honeypot risk).")\
    .register("trading_cooldown")\
    .on("1",title="Trading cooldown function exists",description="The token contract has  trading cooldown function. If there is a trading cooldown function, the user will not be able to sell the token within a certain time or block after buying.")\
    .on("0",title="No trading cooldown function",description="The token contract has no trading cooldown function. If there is a trading cooldown function, the user will not be able to sell the token within a certain time or block after buying.")\
    .register("is_anti_whale")\
    .on("1",title="Anti-whale mechanism exists (Limited number of transactions)",description="There is a limit to the number of token transactions. The number of scam token transactions may be limited (honeypot risk).")\
    .on("0",title="No anti_whale(Unlimited number of transactions)",description="There is no limit to the number of token transactions. The number of scam token transactions may be limited (honeypot risk).")\
    .register("anti_whale_modifiable")\
    .on("1",title="Anti whale can  be modified",description="The maximum trading amount or maximum position can  be modified.")\
    .on("0",title="Anti whale can not be modified",description="The maximum trading amount or maximum position can not be modified")\
    .register("is_blacklisted")\
    .on("1",title="Blacklist function",description="The blacklist function is included. Some addresses may not be able to trade normally (honeypot risk).")\
    .on("0",title="No blacklist",description="The blacklist function is not included. If there is a blacklist, some addresses may not be able to trade normally (honeypot risk).")\
    .register("is_whitelisted")\
    .on("1",title="Whitelist function",description="Having a whitelist function means that, for this contract, some privileged users may have greater advantages in transactions, such as bypassing transaction limits, being exempt from taxes, trading earlier than others, or not being affected by transaction cooldown restrictions.")\
    .on("0",title="No whitelist",description="The whitelist function is not included. If there is a whitelist, some addresses may not be able to trade normally (honeypot risk).")







    is_open_source = safe_get(goPlusResult,"is_open_source")
    is_proxy=safe_get(goPlusResult,"is_proxy")
    is_mintable= safe_get(goPlusResult,"is_mintable")
    can_take_back_ownership=safe_get(goPlusResult,"can_take_back_ownership")
    owner_change_balance=safe_get(goPlusResult,"owner_change_balance")
    hidden_owner=safe_get(goPlusResult,"hidden_owner")
    selfdestruct=safe_get(goPlusResult,"selfdestruct")
    external_call=safe_get(goPlusResult,"external_call")
    gs_tooken = safe_get(goPlusResult,"gas_abuse")
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
    detail_info = {
        "Token_Price": calute_price,
        "FDV": format_number(fdv),
        "M.Cap": format_number(mcap),
        "Max_Supply": format_number(max_supply),
        "Circulation": format_number(circulating_supply),
        "Token_Symbol": token_symbol,
        "Contract_Address": format_string(Contract_Address),  # 按照前四后六进行展示
        "Contract_Creator": format_string(creator_address),  # 按照前四后六进行展示
        "Contract_Owner": format_string(owner_address),  # 按照前四后六进行展示
        "Toker_Holders": holder_count,  # 统计风险项和注意项的总数。
        "Token_Supply": str(top10Banlance),  # 保留小数点后两位展示。直接展示真实数字，不需要进行k m b单位换算。
        "Top10_Holders_Ratio": str(top10_holders_ratio * 100),  # 保留小数点后两位并采用百分比展示。
        "Contract_Source_Code_Verified":registry.format("is_open_source",is_open_source),
        "No_Proxy":registry.format("is_proxy",is_proxy),
        "No_Mint_Function":registry.format("is_mintable",is_mintable),
        "No_Function_Found_That_Retrieves_Ownership":registry.format("can_take_back_ownership",can_take_back_ownership),
        "Owner_Cant_Change_Balance":registry.format("owner_change_balance",owner_change_balance),
        "No_Hidden_Owner":registry.format("hidden_owner",hidden_owner),
        "This_Token_Can_Not_Self_Destruct":registry.format("selfdestruct",selfdestruct),
        "No_External_Call_Risk_Found":registry.format("external_call",external_call),
        "This_Token_Is_Not_A_Gas_Abuser":registry.format("gas_abuse",gs_tooken),
        "Buy_Tax":format_percentage(buy_tax,decimals=2),
        "Sell_Tax":format_percentage(sell_tax,decimals=2),
        "This_Does_Not_Appear_To_Be_A_Honeypot":registry.format("is_honeypot",is_honeypot),
        "No_Codes_Found_To_Suspend_Trading":registry.format("transfer_pausable",transfer_pausable),
        "No_Trading_Cooldown_Function":registry.format("trading_cooldown",trading_cooldown),
        "No_Anti_Whale_Unlimited_Number_Of_Transactions":registry.format("is_anti_whale",is_anti_whale),
        "Anti_Whale_Cannot_Be_Modified":registry.format("anti_whale_modifiable",anti_whale_modifiable),
        "Tax_Cannot_Be_Modified":tax_Cannot_Be_Modified,
        "No_Blacklist":registry.format("is_blacklisted",is_blacklisted),
        "No_Whitelist":registry.format("is_whitelisted",is_whitelisted),
        "No_Tax_Changes_Found_For_Personal_Addresses":personal_Addresses,
        "Dex_And_Liquidity":Dex_And_Liquidity
    }
    # 组织返回基础信息
    return format_and_convert_keys(detail_info)

#其他类型API工具分析
def api_extra_asnyc(selectedType,type_value):
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

    print("symbolResult:", symbolResult)
    print("goPlusResult:", goPlusResult)
    if goPlusResult is not None and symbolResult is not None:
        symbolResult = symbolResult[0]  # 只取第一个数组数据
        response["overview"] = uniongoPlusResultAndsymbolResultOverView(goPlusResult, symbolResult, contract_addresses)
        response["details"] = uniongoPlusResultAndsymbolResultDetails(goPlusResult, symbolResult, contract_addresses)

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
def wrap_del_with_OverView(detail_data):
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

    res = format_and_convert_keys({
        "Project_Name": detail_data.get("project_name", ""),
        "logo": detail_data.get("logo", ""),
        "Token_Symbol": detail_data.get("token_symbol", ""),
        "Token_Price": str(round(price,2)),
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



def handle_type_based_data(type_item, attached_data):
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
                "overview": wrap_del_with_OverView(detail_data),
                "details": wrap_del_with_detail(detail_data),
                "state": state,
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
        # data["detected_intent"] = Intention.deep_research.value #这里需要进行重新验证
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

        handled_result = handle_type_based_data(selectedType, state.attached_data)
        data.update({
            "description":"I have confirmed the information to be queried. Kindly assist in retrieving the relevant data",
            "overview": handled_result.get("overview", {}),
            "details": handled_result.get("details", {}),
            "state": handled_result.get("state", ""),
            "type":handled_result.get("type")
        })
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

