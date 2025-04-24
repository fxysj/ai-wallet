from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from travel_ai.app.config import llm

prompt = PromptTemplate.from_template("""
请根据关键词和性格，生成一个旅游地图链接，包含打卡点位置。
关键词：{keywords}
性格：{persona}
历史上下文信息:{context}
如果历史上下文中包含了旅游地图链接，包含打卡点位置
进行根据上下文作为参考进行生成旅游地图链接，包含打卡点位置
如果历史上下文没有提供 则根据关键词和性格，生成一个旅游地图链接，包含打卡点位置
""")

MapGeneratorChain = prompt | llm | StrOutputParser()

