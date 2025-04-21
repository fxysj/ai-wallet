from langchain_community.callbacks.manager import get_openai_callback
from langchain_openai import ChatOpenAI

import asyncio
from typing import Dict

async def async_invoke_with_callback_and_store(
    llm: ChatOpenAI,
    prompt: str,
    agentState: Dict
) -> str:
    """
    异步调用 LLM，记录 token 使用情况并保存结果到 agentState 中。
    """
    # 注意：这里是普通的 with（同步），不能用 async with！
    with get_openai_callback() as cb:
        response = await llm.ainvoke(prompt)

    agentState["response"] = response.content
    agentState["token_usage"] = {
        "prompt_tokens": cb.prompt_tokens,
        "completion_tokens": cb.completion_tokens,
        "total_tokens": cb.total_tokens,
        "total_cost": cb.total_cost,
    }

    return response.content
if __name__ == '__main__':
    import asyncio
    from app.agents.lib.llm.llm import LLMFactory
    from langchain.prompts import PromptTemplate

    async def main():
        llm = LLMFactory.getDefaultOPENAI()
        agent_state = {}

        p = """你是一个智能助理，分步骤思考：如何制定一个健康的饮食计划？ 下面是饮食主题:{topic}"""
        te = PromptTemplate(
            template=p,
            input_variables=["topic"]
        )
        # 构建模板
        te = PromptTemplate(
            template=p,
            input_variables=["topic"]
        )

        # 正确地传参：使用命名参数（dict 或 keyword argument）
        t = te.format_prompt(topic="11").to_string()

        print(t)


        result = await async_invoke_with_callback_and_store(
            llm,
            t,
            agent_state
        )

        print("最终回复：", result)
        print("Agent 状态内容：", agent_state)

    asyncio.run(main())
