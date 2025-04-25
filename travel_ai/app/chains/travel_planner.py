from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from travel_ai.app.config import llm

prompt = PromptTemplate.from_template("""
你是旅游达人，请根据关键词和性格推荐一个省钱、高效、有趣的5日旅游行程：
关键词：{keywords}
用户性格：{persona}
历史上下文信息:{context}
返回结构严格按照JSON
返回结果严格参考如下:
```json
{{
  "plan_trip": {{
    "第1天": "抵达三亚，入住酒店，游览大东海景区。",
    "第2天": "前往亚龙湾热带天堂森林公园，观赏自然风光。",
    "第3天": "游玩天涯海角风景区，品尝当地美食。",
    "第4天": "参加出海浮潜，体验海岛风情。",
    "第5天": "自由活动，返程。"
  }}
}}
```
""")

TravelPlannerChain = prompt | llm | JsonOutputParser()
