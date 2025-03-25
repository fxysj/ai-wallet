# ------------------------------------------------------------------------------
# TransactionSystem：会话管理与数据处理
# ------------------------------------------------------------------------------
import re
import uuid
from typing import Any, Dict

from pydantic import ValidationError

from app.agents.schemas import WalletTransactionSchemaForm, WalletTransactionSchema


class TransactionSystem:
    @staticmethod
    def new_session() -> dict:
        """创建新会话，初始化数据和历史记录"""
        return {
            "data": WalletTransactionSchemaForm().dict(by_alias=True),
            "history": [],
            "session_id": str(uuid.uuid4())
        }

    @staticmethod
    def validate_field(field: str, value: Any) -> bool:
        """字段验证"""
        rules = {
            "fromAddr": lambda v: re.fullmatch(r"^0x[a-fA-F0-9]{40}$", str(v)),
            "toAddr": lambda v: re.fullmatch(r"^0x[a-fA-F0-9]{40}$", str(v)),
            "txAmount": lambda v: isinstance(v, (int, float)) and v > 0,
            "chainIndex": lambda v: str(v).upper() in {"ETH", "BSC", "TRX"},
            "tokenSymbol": lambda v: str(v).upper() in {"BTC", "ETH", "USDT"},
            "tokenAddress": lambda v: re.fullmatch(r"^0x[a-fA-F0-9]{40}$", str(v))
        }
        return rules.get(field, lambda _: False)(value)

    @staticmethod
    def smart_merge(current: dict, new_response: dict) -> dict:
        """
        智能合并当前数据与链返回的更新数据（取 new_response.data），
        同时记录验证失败信息，并在返回结果中增加 errors 字段。
        """
        merged = current.copy()
        errors: Dict[str, str] = {}
        new_data = new_response.get("data", {})

        for field in ["chainIndex", "fromAddr", "toAddr", "txAmount", "tokenSymbol", "tokenAddress"]:
            new_value = new_data.get(field)
            # 如果新输入为空，则不更新当前字段
            if new_value in ["", None]:
                continue

            # 处理 txAmount 特殊情况（转换为 float）
            if field == "txAmount":
                try:
                    new_value = float(new_value)
                except (ValueError, TypeError):
                    errors[field] = f"金额格式错误: {new_value}"
                    merged[field] = current.get(field, 0.0)
                    continue

            # 如果新值有效，则覆盖，否则记录错误并保留原有有效数据
            if TransactionSystem.validate_field(field, new_value):
                merged[field] = new_value
            else:
                # 如果当前数据有效则保留，否则置空（或置0）
                if TransactionSystem.validate_field(field, current.get(field)):
                    merged[field] = current.get(field)
                else:
                    merged[field] = "" if field in ["chainIndex", "fromAddr", "toAddr", "tokenSymbol", "tokenAddress"] else 0.0
                errors[field] = f"{field}无效"

        try:
            WalletTransactionSchemaForm(**merged)
            merged["errors"] = errors
            return merged
        except ValidationError as e:
            merged["errors"] = errors
            return merged