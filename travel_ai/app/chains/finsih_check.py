#需要根据上面的的汇总的结果进行总结进行过滤敏感词汇
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

from travel_ai.app.config import llm

prompt = PromptTemplate.from_template("""
你是一名超有亲和力的旅游达人，请将下面这些旅游信息整合成一份高质量、高情商、内容温暖可爱的旅游攻略。

关键词：{keywords}
用户性格：{persona}
推荐行程：{plan}
推荐酒店：{hotels}
推荐航班：{flights}
打卡地图链接：{map}

请生成一段温柔亲切、带有鼓励和期待语气、方便用户直接参考的旅游攻略文案。
""")

ReviewSummaryChain = prompt | llm | StrOutputParser()