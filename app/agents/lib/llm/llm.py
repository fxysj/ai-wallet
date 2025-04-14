# 初始化大模型
from langchain_openai import ChatOpenAI
from app.config import settings
class LLMFactory():
    @staticmethod
    def getDefaultDeepSearchOPENAI()->ChatOpenAI:
        llm = ChatOpenAI(
            model="gpt-4o-search-preview",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE_URL
        )
        return llm

    @staticmethod
    def getOpenAI(open_key,url)-> ChatOpenAI:
        print(url)
        # llm = ChatOpenAI(
        #     model="gpt-4o",
        #     temperature=0.3,
        #     openai_api_key=open_key,
        #     openai_api_base=url,
        # )
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=open_key,
            openai_api_base=url,
        )
        return llm
    @staticmethod
    def getDefaultOPENAI()->ChatOpenAI:
        print("OPENAI_BASE_URL:")
        print(settings.OPENAI_API_BASE_URL)
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE_URL
        )
        return llm





