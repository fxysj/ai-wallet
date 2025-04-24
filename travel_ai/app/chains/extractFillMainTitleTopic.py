from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from travel_ai.app.config import llm

prompt = PromptTemplate.from_template("从以下用户的旅游关键词进行填充更加丰富的主题信息：{keywords}")
ExtractFillMainTitleTopic = prompt | llm | StrOutputParser()
