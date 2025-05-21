# utils/jwt_utils.py
from fastapi import Request
from typing import Optional, Dict

from app.agents.toolsUtils.tools import decode_and_validate_jwt

# TODO: 替换为你的配置方式（可以改成从环境变量或配置文件读取）
SECRET_KEY = "fibonacci_blx2024_be_with_you"
ALGORITHM = "HS256"


async def decode_and_validate_jwt_auth(request: Request) -> Optional[Dict]:
    """
    从请求头 Authorization 中提取并校验 JWT Token
    - 校验成功返回 payload
    - 校验失败或缺失返回 None
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.removeprefix("Bearer ").strip()
    return decode_and_validate_jwt(token, SECRET_KEY, [ALGORITHM])

def decode_and_validate_jwt_header(header) -> Optional[Dict]:
    """
    从请求头 Authorization 中提取并校验 JWT Token
    - 校验成功返回 payload
    - 校验失败或缺失返回 None
    """
    auth_header = header
    token = auth_header.removeprefix("Bearer ").strip()
    return decode_and_validate_jwt(token, SECRET_KEY, [ALGORITHM])
