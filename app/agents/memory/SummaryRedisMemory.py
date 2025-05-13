from langchain.memory import ConversationSummaryBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.agents.lib.llm.llm import LLMFactory


class SummaryRedisMemory:
    def __init__(
        self,
        redis_url: str,
        session_id: str,
        max_token_limit: int = 1000,
    ):
        self.session_id = session_id
        self.llm = LLMFactory.getDefaultOPENAI()

        self.chat_history = RedisChatMessageHistory(
            url=redis_url,
            session_id=session_id,
        )

        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            chat_memory=self.chat_history,
            max_token_limit=max_token_limit,
            return_messages=True,
        )

    def ask(self, user_input: str) -> AIMessage:
        # 添加用户输入
        self.chat_history.add_user_message(user_input)

        # 获取摘要历史（为 List[BaseMessage]）
        summary_messages: List[BaseMessage] = self.memory.load_memory_variables({})["history"]

        # 构造新的消息序列
        messages = summary_messages + [HumanMessage(content=user_input)]

        # 调用模型生成回复
        response = self.llm.invoke(messages)

        # 添加 AI 回复
        self.chat_history.add_ai_message(response.content)

        return response

    def get_all_messages(self) -> List[BaseMessage]:
        return self.chat_history.messages

    def clear(self):
        self.chat_history.clear()
