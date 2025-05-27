from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


def format_price_display(price: float) -> str:
    """
    格式化价格显示，根据数值大小自动调整精度

    Args:
        price: 价格数值

    Returns:
        格式化后的价格字符串
    """
    # 处理特殊值
    if price == 0:
        return "0.0"
    if price < 0:
        return f"-{format_price_display(-price)}"
    if not isinstance(price, float) or price in {float('inf'), float('-inf'), float('nan')}:
        raise ValueError(f"Invalid price value: {price}")

    try:
        d = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"Cannot convert price to Decimal: {price}")

    # 处理较大数值
    if d >= Decimal("1"):
        return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    elif d >= Decimal("0.1"):
        return str(d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))
    elif d >= Decimal("0.01"):
        return str(d.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
    elif d >= Decimal("0.001"):
        return str(d.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP))
    elif d >= Decimal("0.0001"):
        return str(d.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
    elif d >= Decimal("0.00001"):
        return str(d.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP))
    else:
        # 极小数处理
        decimal_str = f"{d:.20f}"  # 获取足够长的小数表示
        decimal_part = decimal_str.split('.')[1]  # 获取小数点后的部分

        # 找到第一个非零数字的位置
        first_non_zero = next((i for i, c in enumerate(decimal_part) if c != '0'), None)
        if first_non_zero is None:
            return "0.0"  # 理论上不会执行到这里，因为已经处理过0的情况

        # 提取前三位有效数字
        significant_digits = decimal_part[first_non_zero:first_non_zero + 3]
        # 补零如果不足三位
        significant_digits = significant_digits.ljust(3, '0')

        return f"0.0({first_non_zero}){significant_digits}"


from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


def format_price_display_project(price: float) -> str:
    """
    格式化价格显示，根据数值大小自动调整精度

    Args:
        price: 价格数值

    Returns:
        格式化后的价格字符串
    """
    # 处理特殊值
    if price == 0:
        return "0.0"
    if not isinstance(price, float) or price in {float('inf'), float('-inf'), float('nan')}:
        raise ValueError(f"Invalid price value: {price}")

    # 负数处理：先转为正数格式化，最后加负号
    if price < 0:
        return "-" + format_price_display(-price)

    try:
        d = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"Cannot convert price to Decimal: {price}")

    # 处理较大数值
    if d >= Decimal("1"):
        return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    elif d >= Decimal("0.1"):
        return str(d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))
    elif d >= Decimal("0.01"):
        return str(d.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
    elif d >= Decimal("0.001"):
        return str(d.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP))
    elif d >= Decimal("0.0001"):
        return str(d.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
    elif d >= Decimal("0.00001"):
        return str(d.quantize(Decimal("0.0000001"), rounding=ROUND_HALF_UP))
    else:
        # 极小数处理
        decimal_str = f"{d:.20f}"  # 获取足够长的小数表示
        decimal_part = decimal_str.split('.')[1]  # 获取小数点后的部分

        # 找到第一个非零数字的位置
        first_non_zero = next((i for i, c in enumerate(decimal_part) if c != '0'), None)
        if first_non_zero is None:
            return "0.0"  # 理论上不会执行到这里，因为已经处理过0的情况

        # 提取前三位有效数字
        significant_digits = decimal_part[first_non_zero:first_non_zero + 3]
        # 补零如果不足三位
        significant_digits = significant_digits.ljust(3, '0')

        return f"0.0({first_non_zero}){significant_digits}"
