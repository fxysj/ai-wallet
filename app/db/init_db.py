# app/init_db.py

import asyncio

from sqlalchemy import inspect

from app.db.database import engine, Base
from app.db.agent_record_model import AgentRecord  # 👈 这句很重要！不能漏
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # 检查已创建的表
        def do_inspect(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        tables = await conn.run_sync(do_inspect)
        print(f"✅ 数据库和表已创建，当前存在的表: {tables}")

if __name__ == "__main__":
    asyncio.run(init_models())
