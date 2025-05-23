import asyncio

from app.agents.schemas import AgentState
from app.agents.tasks.send_task import send_task
def callState():
    return AgentState(
        user_input="Hi tikee,I want to initate a transfer.",
        messages=[],
        attached_data={},
        history="",
        langguage="en",
    )

async def main():
    initAgent = callState()
    response = await send_task(initAgent)
    print(response)

if __name__ == '__main__':
    asyncio.run(main())