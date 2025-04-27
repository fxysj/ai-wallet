from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from travel_ai.app.config import llm

prompt = PromptTemplate.from_template("""
请根据关键词和性格，生成一个旅游地图链接，包含打卡点位置。
关键词：{keywords}
性格：{persona}
历史上下文信息:{context}
返回结构严格按照JSON 不要其他格式的结果
返回结果严格参考如下:
```json
{{
  "generate_map": {{
    "map_url": "https://example.com/maps/sanya-trip.png"
  }}
}}
```
""")

MapGeneratorChain = prompt | llm | JsonOutputParser()

