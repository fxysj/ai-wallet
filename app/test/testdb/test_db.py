import asyncio
from sqlalchemy import select
from app.db.database import engine, Base, get_db_session
from app.db.agent_record_model import AgentRecord

async def test_database():
    # ✅ 自动创建表结构
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # ✅ 插入测试数据
    # async for session in get_db_session():
    #     test_record = AgentRecord(
    #         session_id="test123",
    #         user_input="Hello, this is a test.",
    #         attached_data={"source": "test"},
    #         detected_intent="test_intent",
    #         history="",
    #         chain_data={"step": 1},
    #         messages=[{"role": "user", "content": "Hi"}],
    #         result={"ok": True},
    #         langguage="en",
    #         isAsync=True,
    #         thinking_info={"debug": "yes"}
    #     )
    #     session.add(test_record)
    #     await session.commit()
    #
    # # ✅ 查询数据验证
    # async for session in get_db_session():
    #     result = await session.execute(select(AgentRecord).where(AgentRecord.session_id == "test123"))
    #     record = result.scalar_one_or_none()
    #     if record:
    #         print("✅ 查询成功:", record.session_id, record.user_input)
    #     else:
    #         print("❌ 查询失败，未找到记录。")

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_database())
