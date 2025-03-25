from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
class MissField(BaseModel):
    name: str = Field(..., description="缺失字段名称")
    description: str = Field(..., description="缺失字段描述")

class TransactionForm(BaseModel):
    chainIndex: str = Field(..., description="区块链索引")
    fromAddr: str = Field(..., description="来源地址")
    toAddr: str = Field(..., description="目标地址")
    txAmount: float = Field(..., description="转账数量")
    tokenSymbol: str = Field(..., description="数字货币类型")
    tokenAddress: str = Field(..., description="代币合约地址")
    extJson: Optional[str] = Field("", description="额外的 JSON 数据")


class TransactionData(BaseModel):
    state: str = Field(..., description="交易状态，如 '完成' 或 '进行中'")
    intent: str = Field(..., description="用户意图，例如 'send'")
    form: TransactionForm
    missFields: Optional[List[MissField]] = Field([], description="缺失字段列表")
    DxTransActionDetail: Dict[str, Any] = Field({}, description="交易详细信息")


class Message(BaseModel):
    role: str = Field(..., description="消息角色，如 'user' 或 'system'")
    content: str = Field(..., description="消息内容")
    data: Optional[Any] = Field(None, description="可以是任意类型的数据")

class ChatSession(BaseModel):
    session_id: str = Field(..., description="会话 ID")
    messages: List[Message] = Field(..., description="消息列表")



