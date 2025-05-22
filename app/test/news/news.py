#新闻智能体测试
import asyncio
import json

from app.agents.schemas import AgentState
from app.agents.tasks.news_task import getNewSearch
from app.agents.tasks.news_task import news_task
def getNews():
    res = getNewSearch("latest")
    print(json.dumps(res,indent=2, ensure_ascii=False))
def callState():
    return AgentState(
        user_input="查询新闻",
        messages=[],
        attached_data={},
        history="",
        langguage="en",
    )
async def getTask():
    res = await news_task(callState())
    print(res)

if __name__ == '__main__':
   asyncio.run(getTask())