import json
import time
import logging
import random
from typing import Type, Optional
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.config import settings
from pydantic import BaseModel
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 1. 定义返回类型的 Pydantic 模型
class ResponseModel(BaseModel):
    response: str
    status: str = "success"
    additional_info: Optional[str] = None


class Data(BaseModel):
    data: dict


# 2. 创建 PromptTemplate 和 LLM 连接池
class LLMFactory:
    @staticmethod
    def getDefaultOPENAI() -> ChatOpenAI:
        """返回 OpenAI 的 LLM 实例"""
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE_URL
        )


# 3. 限流服务 - Token Bucket (Simple Implementation)
class RateLimiter:
    def __init__(self, max_requests: int, per_seconds: int):
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.tokens = max_requests
        self.timestamp = time.time()
        self.lock = Lock()

    def _reset_tokens(self):
        """Reset tokens if time has passed"""
        now = time.time()
        if now - self.timestamp > self.per_seconds:
            self.tokens = self.max_requests
            self.timestamp = now

    def allow_request(self):
        """Check if a request is allowed, otherwise block or rate limit."""
        with self.lock:
            self._reset_tokens()
            if self.tokens > 0:
                self.tokens -= 1
                return True
            return False


# 4. Circuit Breaker
class CircuitBreaker:
    def __init__(self, failure_threshold: int, recovery_time: int):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failure_count = 0
        self.last_failure_time = 0
        self.is_open = False

    def call(self):
        if self.is_open:
            if time.time() - self.last_failure_time >= self.recovery_time:
                self.reset()
            else:
                logger.warning("Circuit is open, service is down.")
                return False
        return True

    def fail(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.open()

    def open(self):
        self.is_open = True
        self.last_failure_time = time.time()
        logger.warning("Circuit breaker is open, stop calling the service.")

    def reset(self):
        self.is_open = False
        self.failure_count = 0
        logger.info("Circuit breaker reset.")


# 5. Retry Logic
def retry_with_backoff(func, retries: int = 3, delay: float = 2.0):
    """Retry logic with backoff."""
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            logger.error(f"Error on attempt {i + 1}: {e}")
            if i < retries - 1:
                time.sleep(delay * (2 ** i))  # Exponential backoff
            else:
                raise


# 6. JsonOutputParser with Fallback
class JsonOutputParser:
    def parse(self, response: str, response_model: Type[BaseModel]):
        # Log the raw response for debugging
        logger.info(f"Raw response from LLM: {response}")

        try:
            # Try parsing the response as JSON
            response_dict = json.loads(response)
            # Directly assign the JSON data to the model
            return response_model(data=response_dict)
        except json.JSONDecodeError:
            # If the response is not JSON, assign it to the response attribute
            logger.info("Response is not JSON, returning plain text.")
            return response_model(response=response)


# 7. LLMChain with Rate Limiting, Circuit Breaking, and Logging
class LLMChain:
    def __init__(self, pool_size: int = 5, rate_limiter: RateLimiter = RateLimiter(10, 60),
                 circuit_breaker: CircuitBreaker = CircuitBreaker(3, 10)):
        self.pool_size = pool_size
        self.pool = [LLMFactory.getDefaultOPENAI() for _ in range(self.pool_size)]
        self.rate_limiter = rate_limiter
        self.circuit_breaker = circuit_breaker

    def invoke(self, prompt_data: dict, response_model: Type[BaseModel]):
        """执行链式调用：Prompt -> LLM -> JSON Output Parse"""
        if not self.rate_limiter.allow_request():
            logger.warning("Rate limit exceeded. Request blocked.")
            return ResponseModel(response="Rate limit exceeded.", status="error")

        if not self.circuit_breaker.call():
            return ResponseModel(response="Service unavailable due to circuit breaker.", status="error")

        llm = self.pool.pop()  # 获取 LLM 连接
        prompt_template = prompt_data['prompt_template']
        response = prompt_template.format(**prompt_data)

        # Execute LLM request with retry logic
        def llm_request():
            return llm.invoke(response)

        try:
            llm_response = retry_with_backoff(llm_request)
            # Parse JSON response
            parser = JsonOutputParser()
            return parser.parse(llm_response.content, response_model)
        except Exception as e:
            self.circuit_breaker.fail()
            logger.error(f"LLM request failed: {e}")
            return ResponseModel(response="Service failed to respond.", status="error")


# 8. Service Integration
class LLMService:
    def __init__(self, pool_size: int = 5):
        rate_limiter = RateLimiter(10, 60)  # Allow 10 requests per minute
        circuit_breaker = CircuitBreaker(3, 10)  # After 3 failed requests, wait 10 seconds before retrying
        self.chain = LLMChain(pool_size, rate_limiter, circuit_breaker)

    def get_response(self, prompt_data: dict, response_model: Type[BaseModel]):
        """简化外部调用接口"""
        return self.chain.invoke(prompt_data, response_model)


# Example usage
if __name__ == '__main__':
    prompt_template = PromptTemplate(
        template="What is the meaning of life?",
        input_variables=["input"]
    )

    llm_service = LLMService(pool_size=3)  # Set pool size to 3

    # Sample user input data
    prompt_data = {
        "prompt_template": prompt_template,
        "input": "What is the meaning of life?"
    }

    # Get the response from the LLM
    response = llm_service.get_response(prompt_data, ResponseModel)
    print("sss")
    print(response)
