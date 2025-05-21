import asyncio
from app.agents.schemas import AgentState
from app.agents.tasks.receive_task import receive_task

def callState():
    return AgentState(
        user_input="Give me the receiving address.",
        messages=[],
        attached_data={},
        history="",
        langguage="en",
    )

async def main():
    initAgent = callState()
    response = await receive_task(initAgent)
    print(response)

if __name__ == '__main__':
    asyncio.run(main())
