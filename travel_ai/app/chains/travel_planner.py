from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from travel_ai.app.config import llm

prompt = PromptTemplate.from_template("""
你是旅游达人，请根据关键词和性格推荐一个省钱、高效、有趣的5日旅游行程：
关键词：{keywords}
用户性格：{persona}
历史上下文信息:{context}
""")

TravelPlannerChain = prompt | llm | StrOutputParser()
