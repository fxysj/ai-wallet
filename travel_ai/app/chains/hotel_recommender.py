from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from travel_ai.app.config import llm

prompt = PromptTemplate.from_template("""
请根据关键词推荐3家高性价比酒店，列出价格、地点和交通便利性：
关键词：{keywords}
性格：{persona}
历史上下文信息:{context}

返回结构严格按照JSON 不要其他格式的结果
返回结果严格参考如下:
```json
{{
  "recommend_hotel": [
    {{
      "name": "三亚亚龙湾丽思卡尔顿酒店",
      "address": "海南省三亚市亚龙湾国家旅游度假区",
      "price": 1580,
      "rating": 4.8
    }},
    {{
      "name": "三亚香格里拉度假酒店",
      "address": "海南省三亚市海棠湾镇",
      "price": 1200,
      "rating": 4.5
    }}
  ]
}}
```
""")

HotelRecommenderChain = prompt | llm | JsonOutputParser()
