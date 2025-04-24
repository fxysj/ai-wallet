#这里使用 连接池的方式处理
from app.agents.lib.llm.llm_pool import LLMService
from langchain.prompts import PromptTemplate
from pydantic import BaseModel

from app.test.templates.cal import PO

class User(BaseModel):
    info:str

class ResponseModel(BaseModel):
    response:str

service = LLMService(pool_size=3,model_name="gpt-4o")
p =PromptTemplate(
    template=PO,
    input_variables=["birthdate"]
)
Pro = {
    "prompt_template": p,
    "birthdate":"1990-01-01 13:25:34"
}

res = service.get_response(Pro,ResponseModel)
print(res.response)
