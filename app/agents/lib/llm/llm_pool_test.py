from langchain.prompts import PromptTemplate


from app.agents.lib.llm.llm_pool import LLMService, Chain, JsonOutputParser, Data
from pydantic import BaseModel
from typing import Type, Optional


# Dummy response model for testing
class SimpleResponseModel(BaseModel):
    response: str
    status: str = "success"
    additional_info: Optional[str] = None

# Static prompt template for testing
simple_prompt_template = "Please provide a brief health tip."

# Test the response with no dynamic variables
def test_simple_prompt():
    # Setup prompt and LLM service
    prompt_template = PromptTemplate(
        template=simple_prompt_template,
        input_variables=[]
    )

    llm_service = LLMService(pool_size=10)  # Set pool size to 3

    prompt_data = {
        "prompt_template": prompt_template,
        "current_data": None,  # No dynamic data
        "history": None,
        "input": None,
        "langguage": "zh",
        "chain_data": None
    }

    chain = Chain(prompt_template, llm_service.chain.pool[0], JsonOutputParser())
    chain_response = chain.invoke(prompt_data, SimpleResponseModel)

    print(chain_response.model_dump_json())  # Should print the response in the SimpleResponseModel format
    # assert chain_response.response == "Your health tip: Eat a balanced diet and exercise regularly."

test_simple_prompt()




import threading
import time



def test_concurrent_requests():
    # Setup the basic test
    prompt_template = PromptTemplate(
        template="Please provide a health tip based on the following input: {input}",
        input_variables=["input"]
    )

    llm_service = LLMService(pool_size=3)
    state = {
        "input": "I am looking for a diet plan."
    }

    prompt_data = {
        "prompt_template": prompt_template,
        "current_data": None,
        "history": None,
        "input": state["input"],
        "langguage": "zh",
        "chain_data": None
    }
    chain_01 = Chain(prompt_template, llm_service.chain.pool[0], JsonOutputParser())
    # A function to simulate invoking the LLM service concurrently
    def invoke_llm_service_concurrently(prompt_data, response_model, thread_id):
        try:
            chain_response = chain_01.invoke(prompt_data, response_model)
            print(f"Thread {thread_id}: {chain_response.model_dump_json()}")
        except Exception as e:
            print(f"Thread {thread_id} failed: {str(e)}")
    # Creating multiple threads to test concurrency
    threads = []
    for i in range(10):  # Let's test with 10 concurrent requests
        thread = threading.Thread(target=invoke_llm_service_concurrently, args=(prompt_data, SimpleResponseModel, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
if __name__ == '__main__':
  test_concurrent_requests()
