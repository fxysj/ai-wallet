PYTHON_EXECUTOR_TEMPLATE = """
你是一个专业的 Python 代码生成和执行助手，任务如下：
1. **基于用户提供的 `signature`（函数或类定义）和 `description` 生成完整的 Python 代码**。
2. **执行代码，并返回代码字符串和执行结果**。
3. **确保代码符合 Python 语法规范，包含基本错误处理**。

【输入内容】：
- **函数/类签名**: `{signature}`
- **参数**: `{parameters}`
- **描述**: `{description}`（用于描述该函数/类的功能）

【任务要求】：
1. **生成 Python 代码**：
   - **包含 `signature`**，如果是类，则实现 `__init__` 方法。
   - **方法或函数的逻辑**应基于 `description` 生成。
   - **包含错误处理**，确保安全执行。
2. **执行生成的代码**，调用函数/类并传递 `parameters`。
3. **返回 JSON 结构**：
```json
{{
  "generated_code": "生成的 Python 代码字符串",
  "data": "执行结果"
}}
"""

# ---

### **完整代码调用示例**
# ```python
import json
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from app.agents.lib.llm.llm import LLMFactory

if __name__ == '__main__':
    llm = LLMFactory.getDefaultOPENAI()

    prompt = PromptTemplate(
        template=PYTHON_EXECUTOR_TEMPLATE,
        input_variables=["signature", "parameters", "description"],
    )

    chain = prompt | llm | StrOutputParser()

    # 用户输入示例 (函数)
    user_input_func = {
        "signature": "def add_numbers(a: int, b: int) -> int:",
        "parameters": {"a": 10, "b": 20},
        "description": "计算两个整数的和"
    }

    # 用户输入示例 (类)
    user_input_class = {
        "signature": "class RequestUtils:",
        "parameters": {"url": "http://localhost:8000", "method":"GET","headers":{},"path":"/api/v1/test"},
        "description": "实现一个请求工具类 并且支持日志记录功能 返回body content 返回字典"
    }

    def execute_generated_code(user_input):
        """ 调用大模型生成 Python 代码并执行 """
        chain_response = chain.invoke(user_input)

        # 解析 JSON
        response_data =  chain_response
        generated_code = response_data.get("generated_code", "")

        print("\n🔹 生成的代码：\n", generated_code)

        # 执行生成的代码
        local_scope = {}
        exec(generated_code, {}, local_scope)

        signature = user_input["signature"]
        parameters = user_input["parameters"]

        # 解析函数/类名
        if signature.startswith("def "):  # 处理函数
            function_name = signature.split("(")[0].replace("def ", "").strip()
            func = local_scope.get(function_name)
            response_data["data"] = func(**parameters) if callable(func) else "错误：函数未正确定义"

        elif signature.startswith("class "):  # 处理类
            class_name = signature.split(":")[0].replace("class ", "").strip()
            cls = local_scope.get(class_name)
            if cls:
                instance = cls(**parameters)
                method = getattr(instance, "multiply", None)
                response_data["data"] = method() if callable(method) else "错误：未找到 multiply 方法"
            else:
                response_data["data"] = "错误：类未正确定义"

        return response_data

    # 测试执行函数
    #print(execute_generated_code(user_input_func))
    print(execute_generated_code(user_input_class))
