# app/models.py

from sqlalchemy import Column, String, JSON, Boolean, Text
from app.db.database import Base

class AgentRecord(Base):
    __tablename__ = "agent_states"

    session_id = Column(String(64), primary_key=True)
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
