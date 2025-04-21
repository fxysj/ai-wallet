# 初始化大模型
from langchain_openai import ChatOpenAI
from typing import Optional, Union

from langgraph.prebuilt.chat_agent_executor import StructuredResponseSchema

from app.config import settings
from langgraph.prebuilt import create_react_agent

class LLMFactory():
    @staticmethod
    def getDefaultDeepSearchOPENAI() -> ChatOpenAI:
        llm = ChatOpenAI(
            model="gpt-4o-search-preview",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE_URL,
        )
        return llm

    @staticmethod
    def getOpenAI(open_key, url) -> ChatOpenAI:
        print(f"Using OpenAI URL: {url}")
        # 如果有初始状态，就创建一个回调 handler
        # callbacks = []
        # if initial_state is not None:
        #     callbacks.append(ThoughtCaptureHandler(initial_state))

        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=open_key,
            openai_api_base=url,
            # streaming=True,  # 关键：streaming 为 True 才会逐 token 触发 on_llm_new_token
            # callbacks=callbacks
        )
        return llm

    @staticmethod
    def getDefaultOPENAI() -> ChatOpenAI:

        # 如果有初始状态，就创建一个回调 handler
        # callbacks = []
        # if initial_state is not None:
        #     callbacks.append(ThoughtCaptureHandler(initial_state))
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE_URL,
            # streaming=True,  # 关键：streaming 为 True 才会逐 token 触发 on_llm_new_token
            # callbacks=callbacks
        )
        return llm

    @staticmethod
    def create_custom_agent(llm, tools, prompt=None,debug=False,state=None, response_format: Optional[
        Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]]
    ] = None):
        """
        创建一个可注入提示词、LLM 和工具的 React Agent。

        参数：
        - llm: 语言模型（LangChain LLM 实例）
        - tools: 工具列表（LangChain Tool 对象组成的列表）
        - prompt: （可选）PromptTemplate 或字符串，作为 agent 的提示词

        返回：
        - agent: 创建好的 agent 对象
        """
        agent = create_react_agent(llm, tools, prompt=prompt,debug=debug,state_schema=state,response_format=response_format) if prompt else create_react_agent(llm, tools)
        return agent


if __name__ == '__main__':
    initial_state = {}

    llm = LLMFactory.getDefaultOPENAI()

    response = llm.invoke("你是一个智能助理，分步骤思考：如何制定一个健康的饮食计划？")

    print("最终回复：", response.content)
    print("捕获到的思考过程：", initial_state.get("thoughts"))
