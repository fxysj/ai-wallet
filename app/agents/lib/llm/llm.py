# 初始化大模型
from langchain_openai import ChatOpenAI
from app.config import settings
class LLMFactory():
    @staticmethod
    def getOpenAI(open_key,url)-> ChatOpenAI:
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=open_key,
            openai_api_base=url,
        )
        return llm
    @staticmethod
    def getDefaultOPENAI()->ChatOpenAI:
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE_URL
        )
        return llm





