def is_chain_id_60(form):
    return form.get("chainId") == 60


def is_valid_empty_form(form):
    expected = {
        "chainId": 60,
        "fromAddress": "",
        "toAddress": "",
        "slippage": 0.01,
        "tokenAddress": "",
        "rawTx": "",
        "signedTx": ""
    }

    # 检查其他字段是否与期望一致
    for key, expected_value in expected.items():
        if form.get(key) != expected_value:
            return False

    # 特殊处理 amount：允许为 "" 或 0 或 0.0
    amount = form.get("amount")
    if amount not in ("", 0, 0.0):
        return False

    return True
