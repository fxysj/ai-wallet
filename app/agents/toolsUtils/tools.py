import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

def decode_and_validate_jwt(token: str, secret_key: str, algorithms: list) -> dict:
    """
    解码并验证 JWT。

    :param token: JWT 字符串。
    :param secret_key: 用于签名的密钥。
    :param algorithms: 用于解码的算法列表。
    :return: 解码后的 payload，如果验证失败则返回 None。
    """
    try:
        # 解码并验证 JWT
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except ExpiredSignatureError:
        print("Token 已过期")
    except InvalidTokenError:
        print("无效的 Token")
    return None
