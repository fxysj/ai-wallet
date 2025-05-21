# app/middlewares.py
from langgraph.pregel.io import AddableValuesDict
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.db.database import get_db_session
from app.db.agent_record_model import AgentRecord
from app.agents.toolsUtils.jwt_utils import decode_and_validate_jwt_header
class AgentStateSaveMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        auth = decode_and_validate_jwt_header(auth_header)

        response = await call_next(request)

        agent_state = getattr(request.state, "agent_state", None)
        print(agent_state)
        if agent_state:
            try:
                async for session in get_db_session():  # ✅ 注意是 async generator
                    db_obj = AgentRecord(**agent_state)
                    if auth_header:
                        db_obj.jwt_origina = auth_header
                        if auth:
                            db_obj.jwt_decode_obj = auth
                            db_obj.user_id = auth.get("user_id")
                    session.add(db_obj)
                    await session.commit()
                    # 保存成功后调用查询函数
                    records = await self.query_agent_records(session)
                    print(f"保存后查询到 {len(records)} 条记录")
                    for r in records:
                        print("🧾 AgentRecord:")
                        print(f"   🔑 id     : {r.id}")
                        print(f"   😄 user_id: {r.user_id}")
                        print(f"   o(╥﹏╥)o jwt_obj: {r.jwt_decode_obj}")
                        print(f"   🔑 session_id     : {r.session_id}")
                        print(f"   💬 user_input     : {r.user_input}")
                        print(f"   🎯 detected_intent: {r.detected_intent}")
                        print(f"   🌐 language       : {r.langguage}")
                        print(f"   ⚙️  isAsync        : {r.isAsync}")
                        print(f"   📦 result          : {r.result}")
            except Exception as e:
                print(f"❌ 保存 AgentState 失败: {e}")
        return response

        # 修改查询函数，接收 session，复用同一个连接会更好

    async def query_agent_records(self, session):
        try:
            result = await session.execute(
                select(AgentRecord).order_by(AgentRecord.id.desc()).limit(1)
            )
            return result.scalars().all()
        except Exception as e:
            print(f"❌ 查询 AgentRecord 失败: {e}")
            return []
