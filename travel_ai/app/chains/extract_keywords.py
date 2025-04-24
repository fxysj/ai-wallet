from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from travel_ai.app.config import llm

prompt = PromptTemplate.from_template("从以下用户输入中提取旅游相关关键词：{user_input}")
ExtractKeywordChain = prompt | llm | StrOutputParser()
