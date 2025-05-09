#提示词fallback兜底提示词测试
from app.agents.schemas import AgentState
from app.agents.tasks.fallback_task import fallback_task
def callState():
    return AgentState(
        user_input="妈的",
        messages=[],
        attached_data={},
        history="",
    )
def Fallback():
   return fallback_task(callState())

if __name__ == '__main__':
    print(Fallback().result)
