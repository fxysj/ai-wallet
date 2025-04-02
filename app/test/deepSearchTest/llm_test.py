#大模型测试提示词
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory

PYTHON_EXECUTOR_TEMPLATE = """
你是一个 Python 代码生成助手，任务是根据用户提供的数据动态生成 Python 代码，并返回该代码的字符串表示。

【输入内容】：
- 用户提供的函数名: {function_name}
- 用户提供的参数: {parameters}

【任务要求】：
1. 生成一个 Python 函数：
   - 函数名：`{function_name}`
   - 参数：从 `parameters` 的键自动匹配
   - 函数返回计算结果，并带有基础错误处理
2. **不执行代码**，仅返回代码字符串。
3. 确保 Python 语法正确，且结构清晰。

【返回 JSON 结构】：
```json
{{
  "generated_code": "生成的 Python 代码字符串"
}}
"""
### **如何调用**
# 你可以这样使用它：
# ```python
if __name__ == '__main__':
    llm = LLMFactory.getDefaultOPENAI()

    prompt = PromptTemplate(
        template=PYTHON_EXECUTOR_TEMPLATE,
        input_variables=["function_name", "parameters"],
    )

    chain = prompt | llm | JsonOutputParser()

    # 调用链处理用户最新输入
    chain_response = chain.invoke({
        "function_name": "add_numbers",
        "parameters": {
            "a": 10,
            "b": 20
        }
    })

    # 解析 JSON，获取代码字符串
    print(chain_response)
    response_data = chain_response
    generated_code = response_data.get("generated_code", "")

    print("生成的代码：")
    print(generated_code)

    # 执行生成的代码
    local_scope = {}
    exec(generated_code, {}, local_scope)

    # 提取并执行函数
    function_name = "add_numbers"
    func = local_scope.get(function_name)

    if callable(func):
        execution_result = func(**{"a": 10, "b": 20})
        print("执行结果:", execution_result)
    else:
        print("错误：未能正确定义函数")

