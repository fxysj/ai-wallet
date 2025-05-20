import asyncio
from app.agents.schemas import AgentState
from app.agents.tasks.receive_task import receive_task

def callState():
    return AgentState(
        user_input="给我显示solana的收款地址",
        messages=[],
        attached_data={},
        history="",
        langguage="English",
    )

async def main():
    initAgent = callState()
    response = await receive_task(initAgent)
    print(response)

if __name__ == '__main__':
    asyncio.run(main())
