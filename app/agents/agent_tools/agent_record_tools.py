from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from app.agents.services.agent_record_service import AgentRecordService
from app.db.database import async_session_maker

# --- 1. 获取单条记录工具 ---
class GetAgentRecordInput(BaseModel):
    record_id: int = Field(..., description="AgentRecord 的 ID")

class GetAgentRecordTool(BaseTool):
    name: str = "get_agent_record_by_id"
    description: str = "根据 record_id 获取一条 AgentRecord 记录"
    args_schema: Type[BaseModel] = GetAgentRecordInput

    async def _arun(self, record_id: int) -> dict:
        async with async_session_maker() as db:
            service = AgentRecordService(db)
            record = await service.get_record_by_id(record_id)
            print("record", record)
            if record is None:
                return {}
            return {
                "id": record.id,
                "user_id": record.user_id,
                "session_id": record.session_id,
                "user_input": record.user_input,
                "detected_intent": record.detected_intent,
                # 确保不会有 None + int 的情况
            }

    def _run(self, *args, **kwargs):
        raise NotImplementedError("请使用 async 模式")


# --- 2. 分页查询工具 ---
class QueryAgentRecordsInput(BaseModel):
    user_id: Optional[str] = Field(None, description="可选的 user_id 过滤")
    detected_intent: Optional[str] = Field(None, description="可选的意图过滤")
    page: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页大小")

class QueryAgentRecordsTool(BaseTool):
    name: str = "query_agent_records"
    description: str = "分页查询 AgentRecord 记录，可按 user_id 和 intent 过滤"
    args_schema: Type[BaseModel] = QueryAgentRecordsInput

    async def _arun(
        self, user_id: Optional[str] = None, detected_intent: Optional[str] = None, page: int = 1, page_size: int = 10
    ) -> dict:
        async with async_session_maker() as db:
            service = AgentRecordService(db)
            return await service.paginated_query(
                page=page,
                page_size=page_size,
                user_id=user_id,
                detected_intent=detected_intent,
            )

    def _run(self, *args, **kwargs):
        raise NotImplementedError("请使用 async 模式")


# --- 3. 导出 CSV 工具 ---
class ExportAgentRecordsCSVInput(BaseModel):
    user_id: Optional[str] = Field(None, description="可选的用户 ID，用于过滤导出的记录")

class ExportAgentRecordsCSVTool(BaseTool):
    name: str = "export_agent_records_csv"
    description: str = "导出 AgentRecord 记录为 CSV 文件，并返回下载链接"
    args_schema: Type[BaseModel] = ExportAgentRecordsCSVInput

    async def _arun(self, user_id: Optional[str] = None) -> str:
        base_url = "http://localhost:8000/db/v1/agent_record/export/csv"
        if user_id:
            return f"{base_url}?user_id={user_id}"
        return base_url

    def _run(self, *args, **kwargs):
        raise NotImplementedError("请使用 async 模式")


# --- 4. 导出 Excel 工具 ---
class ExportAgentRecordsExcelInput(BaseModel):
    user_id: Optional[str] = Field(None, description="可选的用户 ID，用于过滤导出的记录")

class ExportAgentRecordsExcelTool(BaseTool):
    name: str = "export_agent_records_excel"
    description: str = "导出 AgentRecord 记录为 Excel 文件，并返回下载链接"
    args_schema: Type[BaseModel] = ExportAgentRecordsExcelInput

    async def _arun(self, user_id: Optional[str] = None) -> str:
        base_url = "http://localhost:8000/db/v1/agent_record/export/excel"
        if user_id:
            return f"{base_url}?user_id={user_id}"
        return base_url

    def _run(self, *args, **kwargs):
        raise NotImplementedError("请使用 async 模式")
