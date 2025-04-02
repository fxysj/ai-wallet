from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List, Union, Dict, Any
from enum import Enum


class Intention(str, Enum):
    send = 'send'
    receive = 'receive'
    swap = 'swap'
    buy = 'buy'
    deep_research = 'deep_research'
    account_analysis = 'account_analysis'
    newsletter = 'newsletter'
    unclear = 'unclear'


class WalletTransactionSchema(BaseModel):
    chainIndex: str = Field(..., description="区块链索引（如 ethereum）")
    fromAddr: str = Field(..., description="源地址")
    toAddr: str = Field(..., description="目标地址")
    txAmount: str = Field(..., description="转账数量")
    tokenSymbol: str = Field(..., description="代币符号（如 ETH）")
    tokenAddress: str = Field(..., description="代币合约地址")
    extJson: str = Field(description="扩展JSON数据")


class WalletTransactionSchemaForm(BaseModel):
    chainIndex: str = Field(default="", description="区块链索引（如 ethereum）")
    fromAddr: str = Field(default="", description="源地址")
    toAddr: str = Field(default="", description="目标地址")
    txAmount: str = Field(default="", description="转账数量")
    tokenSymbol: str = Field(default="", description="代币符号（如 ETH）")
    tokenAddress: str = Field(default="", description="代币合约地址")
    extJson: str = Field(default="", description="扩展JSON数据")

    class Config:
        populate_by_name = True


class ReceiveInfoSchema(BaseModel):
    myAddress: str = Field(default="", description="我的钱包地址")
    myChain: str = Field(default="", description="接收链（如 ethereum）")


class SwapTransactionSchema(BaseModel):
    from_: str = Field(default="", alias='from', description="兑换来源资产")
    to: str = Field(default="", description="兑换目标资产")
    amount: float = Field(default="", description="兑换数量")


class BuyInfoSchema(BaseModel):
    cryptoToken: str = Field(default="", description="加密货币名称")
    fiatCurrency: str = Field(default="", description="法定货币名称")
    amount: float = Field(default="", description="购买金额")

    def to_empty_json(self):
        return self.model_dump()


class ResearchInfoSchema(BaseModel):
    topic: str = Field(default="", description="研究主题")


class AnalysisInfoSchema(BaseModel):
    walletAddress: str = Field(default="", description="钱包地址")
    chain: Optional[str] = Field(None, description="区块链（可选）")


class NewsletterInfoSchema(BaseModel):
    topics: List[str] = Field(default="", description="感兴趣的主题列表")
    timeframe: str = Field(default="", description="时间范围（如 daily）")


# LangGrph共享所有链的核心对象
class AgentState(BaseModel):
    user_input: str = ""  # 用户提交信息
    attached_data: Dict = None  # 用户发送附带的表单信息
    detected_intent: Optional[Intention] = None  # 识别出用户的意图枚举
    session_id: str = ""  # 用户会话信息
    history: str = ""#历史信息
    messages: List[Dict] #传递的历史信息是一个数组的字典形式
    result: Any = None #传递内部数据
    langguage:str="中文"#默认语言是中文的方式
    isAsync:bool=False #是否需要分析 默认不需要


class ResearchTopicSchema(BaseModel):
    nextSearchTopic: str = Field(..., description="下一个搜索主题")
    shouldContinue: str = Field(..., description="是否继续研究")
    findings: List[str] = Field(..., description="研究发现列表")


# 统一入口请求信息
class ChatUnionRequest(BaseModel):
    session_id: str = Field(..., description="用户的身份信息")
    user_input: str = Field(..., description="用户输入内容")


# ------------------------------------------------------------------------------
# 数据模型：交易表单（用于存储核心字段）
# ------------------------------------------------------------------------------
class TransactionForm(BaseModel):
    address: str = Field(
        default="",
        pattern=r"^0x[a-fA-F0-9]{40}$",
        description="区块链地址（0x开头42字符）"
    )
    from_: str = Field(
        default="",
        alias="from",
        pattern=r"^0x[a-fA-F0-9]{40}$",
        description="来源地址（0x开头42字符）"
    )
    amount: float = Field(
        default=0.0,
        gt=0,
        description="转账金额（必须大于0）"
    )
    chain: str = Field(
        default="",
        pattern=r"^(ETH|BSC|TRX)$",
        description="区块链网络"
    )
    coin: str = Field(
        default="",
        pattern=r"^(BTC|ETH|USDT)$",
        description="数字货币类型"
    )

    class Config:
        populate_by_name = True


# ------------------------------------------------------------------------------
# 新增模型：完整转账响应（包含额外信息）
# ------------------------------------------------------------------------------
class FullTransactionResponse(BaseModel):
    data: WalletTransactionSchemaForm  # 转账基础响应
    missfield: str  # 缺失的字段信息
    description: str  # 系统自动回复的描述 AI
    is_completed: bool  # 是否填充完成
    detected_intent: str # 当前的阶段


# ------------------------------------------------------------------------------
# 响应模型
# ------------------------------------------------------------------------------
class BaseResponse:
    @staticmethod
    def success(data: Any = None) -> dict:
        return {"code": 200, "message": "Success", "data": data}

    @staticmethod
    def error(code: int, message: str, data: Any = None) -> dict:
        return {"code": code, "message": message, "data": data}
