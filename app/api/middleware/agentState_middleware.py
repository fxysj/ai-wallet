# app/middlewares.py
from langgraph.pregel.io import AddableValuesDict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.db.database import get_db_session
from app.db.agent_record_model import AgentRecord

class AgentStateSaveMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        agent_state = getattr(request.state, "agent_state", None)
        print(agent_state)
        if agent_state:
            try:
                async for session in get_db_session():  # ✅ 注意是 async generator
                    db_obj = AgentRecord(**agent_state)
                    session.add(db_obj)
                    await session.commit()
            except Exception as e:
                print(f"❌ 保存 AgentState 失败: {e}")
        return response
