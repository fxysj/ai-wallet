# app/models.py

from sqlalchemy import Column, String, JSON, Boolean, Text, Integer
from app.db.database import Base

class AgentRecord(Base):
    __tablename__ = "agent_states"
    id = Column(Integer, primary_key=True,autoincrement=True)
    jwt_origina = Column(Text,comment="jwt_origina 原始信息")
    user_id=Column(String(128),comment="用户id")
    jwt_decode_obj=Column(JSON,comment="jwt解析出来的信息")
    session_id = Column(String(64))
    user_input = Column(Text)
    attached_data = Column(JSON)
    detected_intent = Column(String(64))
    history = Column(Text)
    chain_data = Column(JSON)
    messages = Column(JSON)
    result = Column(JSON)
    langguage = Column(String(16))
    isAsync = Column(Boolean)
    thinking_info = Column(JSON)
