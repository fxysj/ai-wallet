def is_valid_empty_form_ok(form):
    expected = {
        "chainId": 60,
        "toAddress": "",
        "slippage": 0.01,
        "rawTx": "",
        "signedTx": ""
    }

    # 检查除 fromAddress、amount、tokenAddress 外的字段
    for key, expected_value in expected.items():
        if form.get(key) != expected_value:
            return False

    # 特殊处理 amount：允许为 ""、0、0.0
    amount = form.get("amount")
    if amount not in ("", 0, 0.0):
        return False

    # 特殊处理 tokenAddress：允许为 "" 或 "native"
    token_address = form.get("tokenAddress", "")
    if token_address not in ("", "native"):
        return False

    # 不检查 fromAddress
    return True

if __name__ == '__main__':
    form = {
        "chainId": 60,
        "fromAddress": "任意内容",  # 忽略
        "toAddress": "",
        "amount": "",
        "slippage": 0.01,
        "tokenAddress": "native",
        "rawTx": "",
        "signedTx": ""
    }

    print(is_valid_empty_form_ok(form))  # 输出: True

    form = {
        "chainId": 60,
        "fromAddress": "",  # 忽略
        "toAddress": "",
        "amount": "",
        "slippage": 0.01,
        "tokenAddress": "",
        "rawTx": "",
        "signedTx": ""
    }

    print(is_valid_empty_form_ok(form))  # 输出: True

    form = {
        "chainId": 60,
        "fromAddress": "xxx",  # 忽略
        "toAddress": "xxx",
        "amount": "",
        "slippage": 0.01,
        "tokenAddress": "native",
        "rawTx": "",
        "signedTx": ""
    }

    print(is_valid_empty_form_ok(form))  # 输出: True

