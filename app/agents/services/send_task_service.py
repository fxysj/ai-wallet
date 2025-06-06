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