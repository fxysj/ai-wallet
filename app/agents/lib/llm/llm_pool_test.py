import json
import time
from typing import Optional

from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

from app.agents.lib.llm.llm_pool import LLMService, ResponseModel


def basic_test():
    prompt_template = PromptTemplate(
        template="What is the meaning of life?",
        input_variables=["input"]
    )
    llm_service = LLMService(pool_size=3)
    prompt_data = {
        "prompt_template": prompt_template,
        "input": "What is the meaning of life?"
    }

    # Get response
    response = llm_service.get_response(prompt_data, ResponseModel)
    print(f"Basic Test Response: {response}")
    assert response.status == "success", "Test failed: Status should be 'success'"



import threading

def concurrent_test():
    def make_request(thread_id):
        prompt_template = PromptTemplate(
            template="Provide a health tip for {input}",
            input_variables=["input"]
        )
        llm_service = LLMService(pool_size=3)
        prompt_data = {
            "prompt_template": prompt_template,
            "input": f"Request {thread_id}"
        }

        response = llm_service.get_response(prompt_data, ResponseModel)
        print(f"Thread {thread_id}: {response}")

    threads = []
    for i in range(10):  # Test with 10 concurrent requests
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def circuit_breaker_test():
    prompt_template = PromptTemplate(
        template="What is the meaning of life?",
        input_variables=["input"]
    )

    llm_service = LLMService(pool_size=3)
    prompt_data = {
        "prompt_template": prompt_template,
        "input": "What is the meaning of life?"
    }

    # Simulate failure by making multiple unsuccessful calls
    for i in range(5):  # Exceed the circuit breaker threshold (3 failures)
        response = llm_service.get_response(prompt_data, ResponseModel)
        print(f"Attempt {i + 1}: {response}")
        assert response.status == "error", "Test failed: Circuit breaker should be triggered"

def complex_case_test():
    prompt_template = PromptTemplate(
        template="Provide a health tip for {input} with additional info {info}",
        input_variables=["input", "info"]
    )

    llm_service = LLMService(pool_size=3)
    prompt_data = {
        "prompt_template": prompt_template,
        "input": "I need to lose weight.",
        "info": "I am 30 years old."
    }

    # Get response
    response = llm_service.get_response(prompt_data, ResponseModel)
    print(f"Complex Case Test Response: {response}")
    assert response.status == "success", "Test failed: Status should be 'success'"

class CustomResponseModel(BaseModel):
    message: str
    result: str

def custom_response_test():
    prompt_template = PromptTemplate(
        template="Tell me something interesting about {input}",
        input_variables=["input"]
    )

    llm_service = LLMService(pool_size=3)
    prompt_data = {
        "prompt_template": prompt_template,
        "input": "space exploration"
    }

    response = llm_service.get_response(prompt_data, CustomResponseModel)
    print(f"Custom Response Test: {response}")
    assert response.result == "success", "Test failed: Custom response model didn't return expected result"

def complex_prompt_test():
    prompt_template = PromptTemplate(
        template="You are an expert in {field}. Please answer the following question: {question}",
        input_variables=["field", "question"]
    )

    llm_service = LLMService(pool_size=3)
    prompt_data = {
        "prompt_template": prompt_template,
        "field": "astronomy",
        "question": "What is a black hole?"
    }

    response = llm_service.get_response(prompt_data, ResponseModel)
    print(f"Complex Prompt Test Response: {response}")
    assert response.status == "success", "Test failed: Status should be 'success'"

def fallback_test():
    prompt_template = PromptTemplate(
        template="What is the meaning of life?",
        input_variables=["input"]
    )

    llm_service = LLMService(pool_size=3)
    prompt_data = {
        "prompt_template": prompt_template,
        "input": "What is the meaning of life?"
    }

    # Simulate an invalid response scenario
    def invalid_response():
        return '{"invalid_response": "no data"}'

    # Replace llm_service.invoke to simulate invalid response
    llm_service.chain.pool[0].invoke = invalid_response
    response = llm_service.get_response(prompt_data, ResponseModel)
    print(f"Fallback Test Response: {response}")
    assert response.status == "error", "Test failed: Fallback should have occurred"

def rate_limiting_test():
    prompt_template = PromptTemplate(
        template="Provide a health tip for {input}",
        input_variables=["input"]
    )

    llm_service = LLMService(pool_size=3)
    prompt_data = {
        "prompt_template": prompt_template,
        "input": "How to improve my fitness?"
    }

    # Simulate multiple requests to exceed rate limit
    for i in range(12):  # Exceed the limit of 10 requests per minute
        response = llm_service.get_response(prompt_data, ResponseModel)
        print(f"Rate Limiting Test Attempt {i + 1}: {response}")
        if i >= 10:
            assert response.status == "error", "Test failed: Rate limiting should block the request"


def test_complex_json_format():
    # 定义复杂的提示词模板
    complex_prompt_template = """
    You are an advanced assistant. Please provide a detailed response in JSON format that includes:
    - 'response': a string, describing the answer to the question.
    - 'metadata': an object with keys:
        - 'timestamp': the current time in seconds since epoch.
        - 'language': the language of the response.
        - 'context': an optional description of the user's inquiry.
    - 'status': a string, either "success" or "error", indicating the status of the response.
    - 'additional_info': optional string, any additional information about the request.

    Respond to the following question: {user_input}
    """

    # 输入数据
    prompt_data = {
        "prompt_template": complex_prompt_template,
        "user_input": "What is the meaning of life?",
        "timestamp": str(int(time.time())),
        "context": "User is seeking a philosophical perspective.",
    }

    # 自定义返回的Pydantic模型
    class ComplexResponseModel(BaseModel):
        response: str
        status: str
        metadata: dict
        additional_info: Optional[str] = None

    # 模拟 LLM 服务调用
    llm_service = LLMService(pool_size=3)

    # 获取响应
    response = llm_service.get_response(prompt_data, ComplexResponseModel)

    # 断言检查
    assert response.status == "success", f"Expected success, got {response.status}"
    assert "response" in response.dict(), "Missing 'response' field"
    assert "metadata" in response.dict(), "Missing 'metadata' field"
    assert "timestamp" in response.metadata, "Missing 'timestamp' in metadata"
    assert "language" in response.metadata, "Missing 'language' in metadata"

    # 输出完整的响应
    print(json.dumps(response.dict(), indent=4))


# 运行测试


if __name__ == "__main__":
    test_complex_json_format()
    # basic_test()
    # concurrent_test()
    # circuit_breaker_test()
    # complex_case_test()
    # custom_response_test()
    # complex_prompt_test()
    # fallback_test()
    # rate_limiting_test()
