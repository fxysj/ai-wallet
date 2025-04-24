from typing import Optional, Any, Dict
from pydantic import BaseModel


class UserState(BaseModel):
    user_id: str #用户id
    user_input: str #用户输入的信息
    persona: Optional[str] = ""#性格信息
    retrieved: Any = None  # 向量数据检索到的文档信息
    keywords:str=""#捕捉到的用户的关键词信息
    plan:Dict =None #计划信息
    hotels:Dict=None#旅馆信息
    flights:Dict=None#航班信息
    map:Dict=None#地图信息
    cute_summary:Dict=None #最后的结果


