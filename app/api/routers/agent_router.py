#这里是涉及agent对应的路由信息
#这里是RAG的路由方式
from typing import AsyncGenerator

from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from app.agents.response.Response import SystemResponse
from app.utuls.Messages import Session

#初始化路由
router = APIRouter()

@router.post("/agent",description="智能助手")
async def query_rag(request: Request):
    request_data = await request.json()
    session_id = request_data.get("session_id")
    id = request_data.get("id")
    messages = request_data.get("messages")
    if id:
        session_id = id
    if not session_id:
        return SystemResponse.error_with_message(
            message="请先进行授权登录钱包",
        )
    # 使用配置的方式进行用户会话隔离
    thread_config = {"configurable": {"thread_id": session_id}}
    user_input_object = Session.get_last_user_message(request_data)
    user_input = user_input_object.content
    # ✅ 从 app.state 获取 travel_graph
    travel_graph = request.app.state.travel_graph
    async def stream_response() -> AsyncGenerator[str, None]:
        output = None
        async for output in travel_graph.astream(
                input=[HumanMessage(content=user_input)],
                config=thread_config,
                stream_mode="updates"
        ):
            last_message = next(iter(output.values()))
            yield f"data: {last_message.content}\n\n"
        if output and "prompt" in output:
            yield "data: Done!\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")