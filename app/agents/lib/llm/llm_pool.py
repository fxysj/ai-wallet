from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.config import settings
from app.agents.lib.llm.callback.CallbackHandler import ThoughtCaptureHandler
from pydantic import BaseModel
from typing import Type, Optional


# 1. 定义返回类型的 Pydantic 模型
class ResponseModel(BaseModel):
    response: str
    status: str = "success"
    additional_info: Optional[str] = None

class Data(BaseModel):
    data: dict


# 2. 创建 PromptTemplate 和 LLM 连接池
class LLMFactory():
    @staticmethod
    def getDefaultOPENAI() -> ChatOpenAI:
        """返回 OpenAI 的 LLM 实例"""
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE_URL
        )


# 3. 创建链式调用（PromptTemplate -> LLM -> JsonOutputParser）
class JsonOutputParser:
    def parse(self, response: str, response_model: Type[BaseModel]):
        """解析 JSON 输出并转换为 Pydantic 模型"""
        return response_model(response=response)


class LLMChain:
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.pool = self._initialize_pool()

    def _initialize_pool(self):
        """初始化连接池"""
        return [LLMFactory.getDefaultOPENAI() for _ in range(self.pool_size)]

    def invoke(self, prompt_data: dict, response_model: Type[BaseModel]):
        """执行链式调用：Prompt -> LLM -> JSON Output Parse"""
        llm = self.pool.pop()  # 获取 LLM 连接
        prompt_template = prompt_data['prompt_template']
        response = prompt_template.format(**prompt_data)

        # 执行 LLM 调用
        llm_response = llm.invoke(response)

        # 解析 JSON 响应并返回模型实例
        parser = JsonOutputParser()
        return parser.parse(llm_response.content, response_model)


# 4. 简化外部调用接口，自动处理链式调用
class LLMService:
    def __init__(self, pool_size: int = 5):
        self.chain = LLMChain(pool_size)

    def get_response(self, prompt_data: dict, response_model: Type[BaseModel]):
        """简化外部调用接口"""
        return self.chain.invoke(prompt_data, response_model)


# 定义链式调用操作符（类似于 langchain 的方式）
class Chain:
    def __init__(self, prompt_template: PromptTemplate, llm, parser: JsonOutputParser):
        self.prompt_template = prompt_template
        self.llm = llm
        self.parser = parser

    def __or__(self, other):
        """定义 | 操作符连接各环节（PromptTemplate -> LLM -> JsonOutputParser）"""
        return Chain(self.prompt_template, self.llm, other)

    def invoke(self, prompt_data: dict, response_model: Type[BaseModel]):
        """执行链式调用"""
        response = self.prompt_template.format(**prompt_data)
        llm_response = self.llm.invoke(response)
        return self.parser.parse(llm_response.content, response_model)


# 示例使用
if __name__ == '__main__':
    from app.agents.proptemts.send_task_propmt_en import PROMPT_TEMPLATE
    prompt_template = PromptTemplate(
        template= PROMPT_TEMPLATE,
        input_variables=["current_data", "history", "input", "langguage", "chain_data"]
    )

    llm_service = LLMService(pool_size=3)  # 设置连接池大小为 3

    # 假设用户的输入数据
    state = {
        "attached_data": "用户最近的健康数据",
        "history": "用户的健康历史",
        "user_input": "我想要一个健康饮食计划",
        "langguage": "zh",
        "chain_data": "其他需要传递的信息"
    }

    # 构造 prompt 数据
    prompt_data = {
        "prompt_template": prompt_template,
        "current_data": state["attached_data"],
        "history": state["history"],
        "input": state["user_input"],
        "langguage": state["langguage"],
        "chain_data": state["chain_data"]
    }

    # 创建链式调用
    chain = Chain(prompt_template, llm_service.chain.pool[0], JsonOutputParser())

    # 调用链处理用户最新输入
    chain_response = chain.invoke(prompt_data, Data)

    # 打印返回的模型实例
    print(chain_response.json())  # 输出符合 Data 格式的 JSON
