from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from travel_ai.app.config import llm

# 定义 PromptTemplate
prompt = PromptTemplate.from_template("""
请根据关键词和用户假期信息推荐经济实用航班：
关键词：{keywords}
历史上下文信息:{context}
返回结构严格按照JSON 不要其他格式的结果
返回结果严格参考如下:
```json
{{
  "recommend_flight": [
    {{
      "airline": "海南航空",
      "departure": "北京首都国际机场 08:30",
      "arrival": "三亚凤凰国际机场 12:10",
      "price": 880
    }},
    {{
      "airline": "南方航空",
      "departure": "上海虹桥 09:00",
      "arrival": "三亚凤凰机场 12:45",
      "price": 980
    }}
  ]
}}
""")
FlightRecommenderChain = prompt | llm | JsonOutputParser()
if __name__ == '__main__':
    input_data = {
        "keywords": "三亚旅游",
        "context": "用户计划在五一假期去三亚旅游"
    }
    result = FlightRecommenderChain.invoke(input_data)
    print(result)