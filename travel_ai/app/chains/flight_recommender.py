from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from travel_ai.app.config import llm

prompt = PromptTemplate.from_template("""
请根据关键词和用户假期信息推荐经济实用航班：
关键词：{keywords}
历史上下文信息:{context}
如果历史上下文中包含了经济实用航班 
进行根据上下文作为参考进行生成经济实用航班
如果历史上下文没有提供 则根据关键词和用户假期信息推荐经济实用航班
""")

FlightRecommenderChain = prompt | llm | StrOutputParser()
