def get_default_form(isSwpRes: str) -> dict:
    """返回指定 isSwpRes 的默认表单配置"""
    return {
        "Swap": {
            "fromChain": "60",
            "fromTokenAddress": "native",
            "toTokenAddress": "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT on Ethereum
            "toChain": "60"
        },
        "Bridge": {
            "fromChain": "60",
            "fromTokenAddress": "native",
            "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",  # USDT on BSC
            "toChain": "56"
        }
    }.get(isSwpRes, {})


def is_form_default(data: dict, isSwpRes: str) -> bool:
    """判断用户是否未主动修改过 form 字段，即是否为默认值或空值"""
    form = data.get("form", {})
    defaults = get_default_form(isSwpRes)

    def is_unmodified_or_empty(value, default):
        return value in [None, "", 0, "0"] or str(value) == str(default)

    return all(
        is_unmodified_or_empty(form.get(k), v)
        for k, v in defaults.items()
    )


def apply_default_form_values(data: dict, isSwpRes: str) -> None:
    """
    如果用户没有主动修改过 form 字段，则根据 isSwpRes 设置默认值。
    """
    if is_form_default(data, isSwpRes):
        data["form"].update(get_default_form(isSwpRes))


def clean_missing_fields_by_form(data: dict) -> None:
    """
    如果 form 中某字段已有有效值，则从 missFields 中删除该字段。
    """
    form = data.get("form", {})
    miss_fields = data.get("missFields", [])

    def is_empty(val):
        return val in [None, "", [], {}, "0", 0]

    # 生成新的 missFields，保留那些在 form 中为空的字段
    data["missFields"] = [
        field for field in miss_fields
        if is_empty(form.get(field["name"]))
    ]