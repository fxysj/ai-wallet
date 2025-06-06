def get_default_form(isSwpRes: str) -> dict:
    return {
        "Swap": {
            "fromChain": "60",
            "fromTokenAddress": "native",
            "toTokenAddress": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "toChain": "60"
        },
        "Bridge": {
            "fromChain": "60",
            "fromTokenAddress": "native",
            "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
            "toChain": "56"
        }
    }.get(isSwpRes, {})


def normalize_value(val):
    if val is None:
        return ""
    if isinstance(val, (int, float)):
        return str(val)
    return str(val).strip().lower()


def is_default_like(val):
    return val in [None, "", [], {}, 0, "0", "native"]


def is_form_default(data: dict, isSwpRes: str) -> bool:
    form = data.get("form", {})
    defaults = get_default_form(isSwpRes)

    for field, default in defaults.items():
        val = form.get(field)

        if field == "fromTokenAddress":
            if normalize_value(val) in ["", "native"]:
                continue
            else:
                return False

        if is_default_like(val):
            continue

        if normalize_value(val) != normalize_value(default):
            return False

    return True


def apply_default_form_values(data: dict, isSwpRes: str) -> None:
    if is_form_default(data, isSwpRes):
        data["form"].update(get_default_form(isSwpRes))


def run_tests():
    print("✅ Running tests...")

    # Test Case 1: 全空字段 => 默认值
    data1 = {
        "form": {
            "fromTokenAddress": "",
            "fromChain": 0,
            "fromAddress": "",
            "toTokenAddress": "",
            "toAddress": "",
            "toChain": 0,
            "amount": 0,
            "slippage": 0.01,
            "disableEstimate": False,
            "signedTx": ""
        }
    }
    assert is_form_default(data1, "Bridge") is True
    apply_default_form_values(data1, "Bridge")
    assert data1["form"]["fromChain"] == "60"
    assert data1["form"]["fromTokenAddress"] == "native"

    # Test Case 2: 字段为默认值 => True
    data2 = {
        "form": {
            "fromTokenAddress": "native",
            "fromChain": "60",
            "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
            "toChain": "56"
        }
    }
    assert is_form_default(data2, "Bridge") is True

    # Test Case 3: 用户修改了其中一个字段 => False
    data3 = {
        "form": {
            "fromTokenAddress": "0x1234567890000000000000000000000000000000",
            "fromChain": "60",
            "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
            "toChain": "56"
        }
    }
    assert is_form_default(data3, "Bridge") is False

    # Test Case 4: fromTokenAddress == "" 也当作默认
    data4 = {
        "form": {
            "fromTokenAddress": "",
            "fromChain": "60",
            "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
            "toChain": "56"
        }
    }
    assert is_form_default(data4, "Bridge") is True

    # Test Case 5: Swap 默认情况
    data5 = {
        "form": {
            "fromTokenAddress": "native",
            "fromChain": "60",
            "toTokenAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7",
            "toChain": "60"
        }
    }
    assert is_form_default(data5, "Swap") is True

    # Test Case 6: Swap 错误 toTokenAddress
    data6 = {
        "form": {
            "fromTokenAddress": "native",
            "fromChain": "60",
            "toTokenAddress": "0x0000000000000000000000000000000000000000",
            "toChain": "60"
        }
    }
    assert is_form_default(data6, "Swap") is False

    print("✅ All tests passed!")


if __name__ == '__main__':
    run_tests()
