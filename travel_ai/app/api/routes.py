import json

from fastapi import APIRouter,Request
from starlette.responses import StreamingResponse

from travel_ai.app.graph.travel_graph import travel_graph
from travel_ai.app.state.user_state import UserState

router = APIRouter()

@router.post("/plan/stream")
async def stream_travel_plan(request: Request):
    data = await request.json()
    user_input = data.get("user_input")
    user_id = data.get("user_id")

    state = UserState(user_id=user_id, user_input=user_input, persona="")

    def generator():
        for step in travel_graph.stream(state):
            yield f"data: {json.dumps(step)}\n\n"

    return StreamingResponse(generator(), media_type="text/event-stream")
