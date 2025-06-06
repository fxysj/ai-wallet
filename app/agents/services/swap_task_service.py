def get_default_form(isSwpRes: str) -> dict:
    """默认配置，chainId 用 int 类型"""
    return {
        "Swap": {
            "fromChain": 60,
            "fromTokenAddress": "native",
            "toTokenAddress": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "toChain": 60
        },
        "Bridge": {
            "fromChain": 60,
            "fromTokenAddress": "native",
            "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
            "toChain": 56
        }
    }.get(isSwpRes, {})


def normalize_value(val):
    """规范值为统一格式（用于比较）"""
    if val is None:
        return ""
    if isinstance(val, (int, float)):
        return str(val)
    return str(val).strip().lower()


def is_default_like(val):
    """判断是否为空或默认类型"""
    return val in [None, "", [], {}, 0, "0", "native"]


def is_form_default(data: dict, isSwpRes: str) -> bool:
    """判断是否与默认表单配置一致"""
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
    """如果当前 form 是默认状态，则填充默认值"""
    if is_form_default(data, isSwpRes):
        data["form"].update(get_default_form(isSwpRes))


def apply_default_form_values_ok(data: dict, isSwpRes: str) -> None:
        data["form"].update(get_default_form(isSwpRes))

def normalize_amount_field(data: dict) -> None:
    """清洗 amount 字段：如果为空或不可用，强制设为 0"""
    form = data.get("form", {})
    amount = form.get("amount")

    if isinstance(amount, str):
        amount = amount.strip()
        if amount == "" or amount == "0":
            form["amount"] = 0
    elif amount in [None]:
        form["amount"] = 0


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
    assert data1["form"]["fromChain"] == 60
    assert data1["form"]["fromTokenAddress"] == "native"

    # Test Case 2: 字段为默认值 => True
    data2 = {
        "form": {
            "fromTokenAddress": "native",
            "fromChain": 60,
            "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
            "toChain": 56
        }
    }
    assert is_form_default(data2, "Bridge") is True

    # Test Case 3: 用户修改了其中一个字段 => False
    data3 = {
        "form": {
            "fromTokenAddress": "0x1234567890000000000000000000000000000000",
            "fromChain": 60,
            "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
            "toChain": 56
        }
    }
    assert is_form_default(data3, "Bridge") is False

    # Test Case 4: fromTokenAddress == "" 也当作默认
    data4 = {
        "form": {
            "fromTokenAddress": "",
            "fromChain": 60,
            "toTokenAddress": "0x55d398326f99059ff775485246999027b3197955",
            "toChain": 56
        }
    }
    assert is_form_default(data4, "Bridge") is True

    # Test Case 5: Swap 默认情况
    data5 = {
        "form": {
            "fromTokenAddress": "native",
            "fromChain": 60,
            "toTokenAddress": "0xdac17f958d2ee523a2206206994597c13d831ec7",
            "toChain": 60
        }
    }
    assert is_form_default(data5, "Swap") is True

    # Test Case 6: Swap 错误 toTokenAddress
    data6 = {
        "form": {
            "fromTokenAddress": "native",
            "fromChain": 60,
            "toTokenAddress": "0x0000000000000000000000000000000000000000",
            "toChain": 60
        }
    }
    assert is_form_default(data6, "Swap") is False

    # Test Case 7: amount 为空字符串，自动设为 0
    data7 = {"form": {"amount": ""}}
    normalize_amount_field(data7)
    assert data7["form"]["amount"] == 0

    print("✅ All tests passed!")


if __name__ == '__main__':
    run_tests()
