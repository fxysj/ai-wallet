# 初始化大模型
from langchain_openai import ChatOpenAI

from app.agents.lib.llm.callback.CallbackHandler import ThoughtCaptureHandler
from app.config import settings


class LLMFactory():
    @staticmethod
    def getDefaultDeepSearchOPENAI() -> ChatOpenAI:
        llm = ChatOpenAI(
            model="gpt-4o-search-preview",
            temperature=0.3,
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

if __name__ == '__main__':
    initial_state = {}

    llm = LLMFactory.getDefaultOPENAI()

    response = llm.invoke("你是一个智能助理，分步骤思考：如何制定一个健康的饮食计划？")

    print("最终回复：", response.content)
    print("捕获到的思考过程：", initial_state.get("thoughts"))
