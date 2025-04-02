# 深度搜索提示词大模型测试
# 对sendTask大模型进行测试
from app.agents.form.form import TaskState
from app.agents.schemas import AgentState, Intention
from app.agents.tasks.send_task import send_task
from app.agents.tasks.swap_task import swap_task
from app.agents.tasks.news_task import news_task
from app.agents.tasks.deep_search_task import research_task
from app.agents.tasks.deep_accunt_analysis import analysis_task
from app.agents.tasks.analysis_task import parse_complex_intent
async def testDeepSearchTask():
    agent = AgentState(
        user_input="我的地址是0x1221",
        session_id="0x1212",
        detected_intent=Intention.send,  # 识别出用户的意图枚举
        history="",
        messages=[],  # 传递的历史信息是一个数组的字典形式
        result={},  # 传递内部数据
        langguage="en",
        isAsync=False,  # 是否需要分析 默认不需要
        attached_data={
            "state": TaskState.SEND_TASK_READY_TO_SIGN,
            "form": {
                "selectedProject": {
                    "id": 12
                },
                "depth": "fast",
                "mode": "1",
                "query": "ETH"
            }
        }
    )
    res = await research_task(agent)
    print(res.result)


async def testNewsTask():
    agent = AgentState(
        user_input="我的地址是0x1221",
        session_id="0x1212",
        detected_intent=Intention.send,  # 识别出用户的意图枚举
        history="",
        messages=[],  # 传递的历史信息是一个数组的字典形式
        result={},  # 传递内部数据
        langguage="en",
        isAsync=False,  # 是否需要分析 默认不需要
        attached_data={
            "state": TaskState.SEND_TASK_READY_TO_SIGN,
            "form": {
                "test": "1.0",
                "tokenAddress": "111",
                "timeframe": "daily"
            }
        }
    )
    res = await news_task(agent)
    print(res.result)


# 测试交换逻辑
async def testSwapTask():
    agent = AgentState(
        user_input="我的地址是0x1221",
        session_id="0x1212",
        detected_intent=Intention.send,  # 识别出用户的意图枚举
        history="",
        messages=[],  # 传递的历史信息是一个数组的字典形式
        result={},  # 传递内部数据
        langguage="en",
        isAsync=False,  # 是否需要分析 默认不需要
        attached_data={
            "state": TaskState.SWAP_TASK_NEED_MORE_INFO,
            "form": {
                "fromTokenAddress": "1111",
                "fromChain": "0x1212",
                "fromAddress": "更新后的值",
                "toTokenAddress": "1111",
                "toAddress": "更新后的值",
                "toChain": "0x12123",
                "amount": "3",
                "slippage": "0.01",
                "disableEstimate": "更新后的值 默认为空字符串",
                "signedTx": "更新后的值 默认为空字符串"
            }
        }
    )
    res = await swap_task(agent)
    print(res.result)


async def testSendTask():
    agent = AgentState(
        user_input="我的地址是0x1221",
        session_id="0x1212",
        detected_intent=Intention.send,  # 识别出用户的意图枚举
        history="",
        messages=[],  # 传递的历史信息是一个数组的字典形式
        result={},  # 传递内部数据
        langguage="en",
        isAsync=False,  # 是否需要分析 默认不需要
        attached_data={
            "state": TaskState.SEND_TASK_READY_TO_SIGN,
            "form": {
                "test": "1.0",
                "tokenAddress": "111"
            }
        }
    )
    res = await send_task(agent)
    print(res.result)

async def testAccountTask():
    agent = AgentState(
        user_input="我的地址是0x1221",
        session_id="0x1212",
        detected_intent=Intention.send,  # 识别出用户的意图枚举
        history="",
        messages=[],  # 传递的历史信息是一个数组的字典形式
        result={},  # 传递内部数据
        langguage="en",
        isAsync=False,  # 是否需要分析 默认不需要
        attached_data={
            "state": TaskState.SEND_TASK_READY_TO_SIGN,
            "form": {
                "account": [{
                    "id":"0x112",
                    "chainId":52,
                    "address":"0x1212",
                }]
            }
        }
    )
    res = await analysis_task(agent)
    print(res.result)


async def testIntentionTask():
    agent = AgentState(
        user_input="分析一下我的地址",
        session_id="0x1212",
        detected_intent=Intention.send,  # 识别出用户的意图枚举
        history="",
        messages=[],  # 传递的历史信息是一个数组的字典形式
        result={},  # 传递内部数据
        langguage="en",
        isAsync=False,  # 是否需要分析 默认不需要
        attached_data={
            "state": TaskState.SEND_TASK_READY_TO_SIGN,
            "form": {
                "account": [{
                    "id":"0x112",
                    "chainId":52,
                    "address":"0x1212",
                }]
            }
        }
    )
    res = await parse_complex_intent(agent)
    print(res.result)
async def main():
    # await testSendTask()  # 正确使用 await 调用
    # await testSwapTask()
    # await testNewsTask()
    #await testDeepSearchTask()
    #await testAccountTask()
    await testIntentionTask()
    #


import asyncio

asyncio.run(main())
