import math

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, and_
from app.db.agent_record_model import AgentRecord
from typing import List, Optional
import pandas as pd
import csv
import io
from fastapi.responses import StreamingResponse
import json

class AgentRecordService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_record(self, data: dict) -> AgentRecord:
        record = AgentRecord(**data)
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_record_by_id(self, record_id: int) -> Optional[AgentRecord]:
        result = await self.db.execute(
            select(AgentRecord).where(AgentRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def update_record(self, record_id: int, update_data: dict) -> Optional[AgentRecord]:
        record = await self.get_record_by_id(record_id)
        if not record:
            return None
        for key, value in update_data.items():
            setattr(record, key, value)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def delete_record(self, record_id: int) -> bool:
        result = await self.db.execute(delete(AgentRecord).where(AgentRecord.id == record_id))
        await self.db.commit()
        return result.rowcount > 0

    async def list_records(self, skip: int = 0, limit: int = 100) -> List[AgentRecord]:
        result = await self.db.execute(
            select(AgentRecord).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def batch_get_by_user_id(self, user_id: str) -> List[AgentRecord]:
        result = await self.db.execute(
            select(AgentRecord).where(AgentRecord.user_id == user_id)
        )
        return result.scalars().all()

    async def export_records(self, user_id: Optional[str] = None) -> str:
        if user_id:
            records = await self.batch_get_by_user_id(user_id)
        else:
            records = await self.list_records(limit=1000)

        export_data = []
        for r in records:
            export_data.append({
                "id": r.id,
                "user_id": r.user_id,
                "session_id": r.session_id,
                "user_input": r.user_input,
                "detected_intent": r.detected_intent,
                "result": r.result,
                "thinking_info": r.thinking_info,
            })

        return json.dumps(export_data, ensure_ascii=False, indent=2)

    async def paginated_query(
            self,
            page: int = 1,
            page_size: int = 10,
            user_id: Optional[str] = None,
            detected_intent: Optional[str] = None
    ) -> dict:
        filters = []
        if user_id:
            filters.append(AgentRecord.user_id == user_id)
        if detected_intent:
            filters.append(AgentRecord.detected_intent == detected_intent)

        stmt = select(AgentRecord).where(and_(*filters)) if filters else select(AgentRecord)

        # Get total count
        count_stmt = stmt.with_only_columns([AgentRecord.id])
        total_result = await self.db.execute(count_stmt)
        total = len(total_result.scalars().all())

        # Apply pagination
        offset = (page - 1) * page_size
        result = await self.db.execute(
            stmt.order_by(AgentRecord.id.desc()).offset(offset).limit(page_size)
        )
        records = result.scalars().all()

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size),
            "data": [r.__dict__ for r in records]
        }

    async def export_to_csv(self, user_id: Optional[str] = None) -> StreamingResponse:
        records = await self.batch_get_by_user_id(user_id) if user_id else await self.list_records()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "user_id", "session_id", "user_input",
            "detected_intent", "langguage", "isAsync", "result"
        ])
        for r in records:
            writer.writerow([
                r.id, r.user_id, r.session_id, r.user_input,
                r.detected_intent, r.langguage, r.isAsync, json.dumps(r.result, ensure_ascii=False)
            ])

        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=agent_records.csv"
        })

    async def export_to_excel(self, user_id: Optional[str] = None) -> StreamingResponse:
        records = await self.batch_get_by_user_id(user_id) if user_id else await self.list_records()

        data = []
        for r in records:
            data.append({
                "ID": r.id,
                "User ID": r.user_id,
                "Session ID": r.session_id,
                "User Input": r.user_input,
                "Intent": r.detected_intent,
                "Lang": r.langguage,
                "Async": r.isAsync,
                "Result": json.dumps(r.result, ensure_ascii=False)
            })

        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="AgentRecords")

        output.seek(0)
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={
                                     "Content-Disposition": "attachment; filename=agent_records.xlsx"
                                 })

