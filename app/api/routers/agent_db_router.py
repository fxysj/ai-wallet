from fastapi import APIRouter, Depends, Query,Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Optional
from fastapi.responses import StreamingResponse

from app.agents.agent.sql_agent import get_sql_agent
from app.db.database import get_db_session
from app.agents.services.agent_record_service import AgentRecordService

router = APIRouter()

@router.post("/agent_record", summary="创建 AgentRecord", description="创建一条新的 AgentRecord 记录。")
async def create(
    data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    """
    创建一条新的 AgentRecord 记录。

    - **data**: 请求体中包含的记录数据，JSON 格式。
    """
    service = AgentRecordService(db)
    return await service.create_record(data)

@router.get("/agent_record/{record_id}", summary="获取 AgentRecord 详情", description="根据记录 ID 获取单条 AgentRecord 数据。")
async def get_record(
    record_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    获取指定 ID 的 AgentRecord。

    - **record_id**: AgentRecord 主键 ID。
    """
    service = AgentRecordService(db)
    return await service.get_record_by_id(record_id)

@router.get("/agent_record/page", summary="分页查询 AgentRecord", description="分页获取 AgentRecord 数据列表，支持按 user_id 和 detected_intent 筛选。")
async def get_records_paginated(
    page: int = Query(1, ge=1, description="页码（从 1 开始）"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数（最大 100）"),
    user_id: Optional[str] = Query(None, description="可选的用户 ID 筛选"),
    detected_intent: Optional[str] = Query(None, description="可选的意图类型筛选"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    分页获取 AgentRecord 列表。

    - **page**: 页码，从 1 开始。
    - **page_size**: 每页数量，最大为 100。
    - **user_id**: （可选）按用户 ID 筛选。
    - **detected_intent**: （可选）按意图字段筛选。
    """
    service = AgentRecordService(db)
    return await service.paginated_query(
        page=page,
        page_size=page_size,
        user_id=user_id,
        detected_intent=detected_intent
    )

@router.get(
    "/agent_record/export/csv",
    summary="导出 AgentRecord 为 CSV",
    description="导出 AgentRecord 记录为 CSV 文件，可选按 user_id 过滤。",
    response_class=StreamingResponse
)
async def download_csv(
    user_id: Optional[str] = Query(None, description="可选的用户 ID 筛选"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    导出 AgentRecord 数据为 CSV 文件。

    - **user_id**: （可选）按用户 ID 筛选导出。
    """
    service = AgentRecordService(db)
    return await service.export_to_csv(user_id)

@router.get(
    "/agent_record/export/excel",
    summary="导出 AgentRecord 为 Excel",
    description="导出 AgentRecord 记录为 Excel 文件，可选按 user_id 过滤。",
    response_class=StreamingResponse
)
async def download_excel(
    user_id: Optional[str] = Query(None, description="可选的用户 ID 筛选"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    导出 AgentRecord 数据为 Excel 文件。

    - **user_id**: （可选）按用户 ID 筛选导出。
    """
    service = AgentRecordService(db)
    return await service.export_to_excel(user_id)

@router.get("/agent_record/agent/query", summary="通过 Agent 查询", description="通过自然语言调用 SQL Agent 执行查询任务。")
async def agent_query(
    q: str = Query(..., description="自然语言查询指令，例如：'导出 user_id 为 xxx 的记录为 CSV'"),
):
    """
    使用 LangChain SQL Agent，通过自然语言进行智能查询。

    - **q**: 自然语言输入，例如 “查找 user_id 为 xxx 的记录并导出为 Excel”。
    """
    try:
        agent_executor = get_sql_agent()
        result = await agent_executor.ainvoke( {"messages": [{"role": "user", "content": q}]})
        return {"success": True, "result":result["structured_response"]}
    except Exception as e:
        return {"success": False, "error": str(e)}