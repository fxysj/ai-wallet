import urllib.parse


def generate_qr_code(address, chain, amount):
    # 定义链的 URI 格式
    if chain.lower() == 'bsc' or chain.lower() == 'ethereum':
        value_wei = int(amount * 10 ** 18)  # BNB 或 ETH 转换为 wei
        uri = f"ethereum:{address}?value={value_wei}"  # Ethereum 和 BSC 使用相同格式
    elif chain.lower() == 'tron':
        # 对于 TRON，可以生成类似这种的 URI
        uri = f"tron:{address}?amount={int(amount * 1e6)}"  # TRON 通常使用 SUN（1 TRX = 1e6 SUN）
    elif chain.lower() == 'solana':
        # Solana 通常以地址为主，没有标准的金额字段，但可以通过其他参数实现（例如 token）。
        uri = f"solana:{address}?amount={int(amount)}"  # Solana 可使用类似格式，但需根据具体需求调整
    elif chain.lower() == 'litecoin':
        # Litecoin 使用与比特币相同的 URI 格式
        value_satoshis = int(amount * 1e8)  # Litecoin 使用 satoshis 为单位
        uri = f"litecoin:{address}?amount={value_satoshis}"
    else:
        raise ValueError("Unsupported chain type. Please use 'BSC', 'Ethereum', 'Tron', 'Solana', or 'Litecoin'.")

    # URL 编码
    encoded_uri = urllib.parse.quote(uri)

    # 生成二维码 API URL
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?data={encoded_uri}&size=200x200"

    return qr_code_url

if __name__ == '__main__':
    # 示例用法
    address = "0x12121323"  # 这里可以替换为任何有效的地址
    chain = "solana"  # 或 "Ethereum", "Tron", "Solana", "Litecoin"
    amount = 0.01  # 你想要的金额（单位：BNB 或 ETH 或其他链的主链币）

    qr_code_url = generate_qr_code(address, chain, amount)
    print(f"二维码链接：{qr_code_url}")


