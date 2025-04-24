from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from travel_ai.app.config import llm

prompt = PromptTemplate.from_template("""
请根据关键词推荐3家高性价比酒店，列出价格、地点和交通便利性：
关键词：{keywords}
性格：{persona}
历史上下文信息:{context}
如果历史上下文中包含了3家高性价比酒店，列出价格、地点和交通便利性
进行根据上下文作为参考进行生成3家高性价比酒店，列出价格、地点和交通便利性
如果历史上下文没有提供 则根据关键词推荐3家高性价比酒店，列出价格、地点和交通便利性
""")

HotelRecommenderChain = prompt | llm | StrOutputParser()
