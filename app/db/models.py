from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RequestLog(Base):
    """存储 API 请求日志"""
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    method = Column(String(10), nullable=False)  # 请求方法 (GET/POST等)
    url = Column(Text, nullable=False)  # 请求 URL
    headers = Column(Text, nullable=True)  # 请求头
    request_body = Column(Text, nullable=True)  # 请求体
    response_body = Column(Text, nullable=True)  # 响应数据
    status_code = Column(Integer, nullable=False)  # HTTP 状态码
    duration = Column(Float, nullable=False)  # 请求耗时
    timestamp = Column(Integer, nullable=False)  # 记录时间戳
