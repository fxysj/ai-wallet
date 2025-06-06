def is_chain_id_60(form):
    return form.get("chainId") == 60


def is_valid_empty_form(form):
    expected = {
        "chainId": 60,
        "fromAddress": "",
        "toAddress": "",
        "amount": 0.0,
        "slippage": 0.01,
        "tokenAddress": "",
        "rawTx": "",
        "signedTx": ""
    }

    for key, expected_value in expected.items():
        if form.get(key) != expected_value:
            return False
    return True


def is_valid_empty_form_ok(form):
    expected = {
        "chainId": 60,
        "toAddress": "",
        "slippage": 0.01,
        "tokenAddress": "",
        "rawTx": "",
        "signedTx": ""
    }

    # 检查除 fromAddress 和 amount 外的字段
    for key, expected_value in expected.items():
        if form.get(key) != expected_value:
            return False

    # 特殊处理 amount：允许为 ""、0、0.0
    amount = form.get("amount")
    if amount not in ("", 0, 0.0):
        return False

    # 不检查 fromAddress，跳过它
    return True

if __name__ == '__main__':
    form = {
        "chainId": 60,
        "fromAddress": "任意内容",  # 不影响结果
        "toAddress": "xx",
        "amount": "xx",
        "slippage": 0.01,
        "tokenAddress": "",
        "rawTx": "",
        "signedTx": ""
    }

    print(is_valid_empty_form_ok(form))
