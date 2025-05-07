# FastAPI 入口
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy import inspect
import uvicorn
from app.api.chat_api import router as chat_router
from app.api.routers.agent_router import router as agent_router
from app.api.exceptions.register import register_exception_handlers
from app.api.middleware.agentState_middleware import AgentStateSaveMiddleware
from app.api.middleware.cores_middleware import setup_cors_middleware
from fastapi import FastAPI
from app.db.database import engine, Base
from psycopg_pool import AsyncConnectionPool
from app.graphs.virtual_assistant_graph import workflow
# 全局变量存放组件（避免多次初始化）
pool = None
checkpointer = None
travel_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    DB_URI = "postgresql://postgres:postgres@pgsql:5432/postgres?sslmode=disable"
    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
    }

    pool = AsyncConnectionPool(
        conninfo=DB_URI,
        max_size=20,
        kwargs=connection_kwargs,
    )
    await pool.__aenter__()

    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()
    travel_graph = workflow.compile(checkpointer=checkpointer)

    # ✅ 将 travel_graph 和其他资源注入 app.state
    app.state.pool = pool
    app.state.checkpointer = checkpointer
    app.state.travel_graph = travel_graph
    yield
    await pool.__aexit__(None, None, None)


    # ✅ 在服务启动时初始化数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据库表结构已初始化")

        # 检查已创建的表
        def do_inspect(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        tables = await conn.run_sync(do_inspect)
        print(f"✅ 数据库和表已创建，当前存在的表: {tables}")

    yield  # 应用运行期间

    # 👇 可选：在服务关闭前执行清理
    print("🛑 FastAPI 应用即将关闭")

# 绑定 lifespan
app = FastAPI(title="区块链智能助手 Pro",
              description="提供转账、查询余额等功能",
              version="1.0.0",lifespan=lifespan)


#设置请求后响应日志stateAgent采集
# app.add_middleware(AgentStateSaveMiddleware)
#设置跨域
app = setup_cors_middleware(app)
# 注册 API
app.include_router(chat_router, prefix="/api/v1")
app.include_router(agent_router,prefix="/api/v1/travel")
#注册异常拦截器
register_exception_handlers(app)



# 启动服务
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
