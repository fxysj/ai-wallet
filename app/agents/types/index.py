from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class WalletTransaction(BaseModel):
    chain_index: str
    from_addr: str
    to_addr: str
    tx_amount: str
    token_symbol: str
    token_address: str
    ext_json: str

class TransactionDetails(BaseModel):
    from_: Optional[str] = Field(None, alias='from')
    to: Optional[str] = None
    amount: Optional[str] = None
    estimatedGas: Optional[str] = None
    chainId: Optional[str] = None
    tokenSymbol: Optional[str] = None
    tokenAddress: Optional[str] = None
    # 其他任意字段
    class Config:
        extra = "allow"



class TaskAction(str, Enum):
    # Common actions
    DISPLAY_GENERAL_ASSISTANCE = 'DISPLAY_GENERAL_ASSISTANCE'
    REQUEST_MORE_INFO = 'REQUEST_MORE_INFO'

    # Transaction actions
    READY_TO_SIGN_TRANSACTION = 'READY_TO_SIGN_TRANSACTION'
    TRANSACTION_BROADCASTED = 'TRANSACTION_BROADCASTED'
    TRANSACTION_FAILED = 'TRANSACTION_FAILED'
    TRANSACTION_CANCELLED = 'TRANSACTION_CANCELLED'

    # Receive actions
    DISPLAY_QR_CODE = 'DISPLAY_QR_CODE'

    # Swap actions
    EXECUTE_SWAP = 'EXECUTE_SWAP'
    CONFIRM_SWAP = 'CONFIRM_SWAP'
    CANCEL_SWAP = 'CANCEL_SWAP'
    EDIT_SWAP = 'EDIT_SWAP'
    RETRY_SWAP = 'RETRY_SWAP'

    # Buy actions
    PURCHASE_CRYPTO = 'PURCHASE_CRYPTO'
    CONFIRMED_PURCHASE = 'CONFIRMED_PURCHASE'
    CANCEL_PURCHASE = 'CANCEL_PURCHASE'
    MODIFY_PURCHASE = 'MODIFY_PURCHASE'

    # Research actions
    DISPLAY_RESEARCH = 'DISPLAY_RESEARCH'

    # Newsletter actions
    DISPLAY_NEWSLETTER = 'DISPLAY_NEWSLETTER'

    # Analysis actions
    DISPLAY_ANALYSIS = 'DISPLAY_ANALYSIS'

class MissingField(BaseModel):
    name: str = Field(..., description="缺失字段名称")
    type: str = Field(..., description="字段类型")
    description: str = Field(..., description="字段描述")

class BaseTaskResult(BaseModel):
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="操作结果消息")
    promptedAction: Optional[List[str]] = Field(None, description="建议的下一步操作")
    action: Union[TaskAction, str] = Field(..., description="执行的操作类型")
    alreadyCollectedParams: Optional[Dict[str, Any]] = Field(None, description="跨步骤收集的数据")

class SendTaskResult(BaseTaskResult):
    action: Union[
        TaskAction.READY_TO_SIGN_TRANSACTION,
        TaskAction.TRANSACTION_BROADCASTED,
        TaskAction.TRANSACTION_FAILED,
        TaskAction.REQUEST_MORE_INFO,
        TaskAction.TRANSACTION_CANCELLED,
        str
    ] = Field(..., description="操作类型")
    missingFields: Optional[List[MissingField]] = Field(None, description="缺失字段列表")
    data: Optional[Dict[str, Any]] = Field(None, description="交易相关数据")

class ReceiveTaskResult(BaseTaskResult):
    action: Union[
        TaskAction.DISPLAY_QR_CODE,
        TaskAction.REQUEST_MORE_INFO,
        str
    ] = Field(..., description="操作类型")
    missingFields: Optional[List[MissingField]] = Field(None, description="缺失字段列表")
    data: Optional[Dict[str, Any]] = Field(None, description="接收相关数据")

class SwapTaskResult(BaseTaskResult):
    action: Union[
        TaskAction.EXECUTE_SWAP,
        TaskAction.REQUEST_MORE_INFO,
        TaskAction.CONFIRM_SWAP,
        TaskAction.CANCEL_SWAP,
        TaskAction.EDIT_SWAP,
        TaskAction.TRANSACTION_BROADCASTED,
        TaskAction.TRANSACTION_FAILED,
        TaskAction.TRANSACTION_CANCELLED,
        TaskAction.RETRY_SWAP,
        str
    ] = Field(..., description="操作类型")
    missingFields: Optional[List[MissingField]] = Field(None, description="缺失字段列表")
    data: Optional[Dict[str, Any]] = Field(None, description="兑换相关数据")

class BuyTaskResult(BaseTaskResult):
    action: Union[
        TaskAction.PURCHASE_CRYPTO,
        TaskAction.REQUEST_MORE_INFO,
        TaskAction.CONFIRMED_PURCHASE,
        TaskAction.CANCEL_PURCHASE,
        TaskAction.MODIFY_PURCHASE,
        str
    ] = Field(..., description="操作类型")
    missingFields: Optional[List[MissingField]] = Field(None, description="缺失字段列表")
    data: Optional[Dict[str, Any]] = Field(None, description="购买相关数据")

class ResearchTaskResult(BaseTaskResult):
    action: Union[
        TaskAction.DISPLAY_RESEARCH,
        str
    ] = Field(..., description="操作类型")
    data: Optional[Dict[str, Any]] = Field(None, description="研究相关数据")

class NewsHeadline(BaseModel):
    title: str = Field(..., description="新闻标题")
    summary: str = Field(..., description="新闻摘要")
    url: Optional[str] = Field(None, description="新闻链接")
    source: Optional[str] = Field(None, description="新闻来源")
    published: Optional[str] = Field(None, description="发布时间")

class NewsletterTaskResult(BaseTaskResult):
    action: Union[
        TaskAction.DISPLAY_NEWSLETTER,
        str
    ] = Field(..., description="操作类型")
    data: Optional[Dict[str, Any]] = Field(None, description="新闻通讯相关数据")

class AnalysisTaskResult(BaseTaskResult):
    action: Union[
        TaskAction.DISPLAY_ANALYSIS,
        str
    ] = Field(..., description="操作类型")
    data: Optional[Dict[str, Any]] = Field(None, description="分析相关数据")

class GeneralAssistantTaskResult(BaseTaskResult):
    action: Union[
        TaskAction.DISPLAY_GENERAL_ASSISTANCE,
        str
    ] = Field(..., description="操作类型")
    data: Optional[Dict[str, Any]] = Field(None, description="通用助理相关数据")

TaskResult = Union[
    SendTaskResult,
    ReceiveTaskResult,
    SwapTaskResult,
    BuyTaskResult,
    ResearchTaskResult,
    NewsletterTaskResult,
    AnalysisTaskResult,
    GeneralAssistantTaskResult
]