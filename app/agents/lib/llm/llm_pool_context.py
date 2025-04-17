from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.extension.chain import ChainNode
from app.agents.lib.llm.extension.chain_executor import ChainExecutor
from app.agents.lib.llm.extension.event import EventDispatcher, LLMEvent
from app.agents.lib.llm.extension.telemetry import LLMTelemetry
from app.agents.lib.llm.llm_pool import EnhancedLLMService, ResponseModel


async def example_usage():
    # 创建服务实例
    service = EnhancedLLMService(pool_size=3)

    # 注册事件处理器
    event_dispatcher = EventDispatcher()

    @event_dispatcher.register_handler("llm_request")
    async def handle_request(event: LLMEvent):
        print(f"Request received at {event.timestamp}: {event.data}")

    @event_dispatcher.register_handler("llm_response")
    async def handle_response(event: LLMEvent):
        print(f"Response received at {event.timestamp}: {event.data}")

    # 创建提示模板
    prompt_template = PromptTemplate(
        template="What is the meaning of life?",
        input_variables=["input"]
    )

    # 准备输入数据
    prompt_data = {
        "prompt_template": prompt_template,
        "input": "What is the meaning of life?"
    }

    # 获取响应
    response = await service.get_response(prompt_data, ResponseModel)
    print(response)
    # 获取指标
    telemetry = LLMTelemetry()
    metrics = telemetry.get_metrics()
    print("Metrics:", metrics)


# 创建更复杂的链式调用示例
async def chain_example():
    service = EnhancedLLMService(pool_size=3)

    # 创建节点
    summarize_node = ChainNode("gpt-4", "Summarize this: {input}")
    translate_node = ChainNode("gpt-3.5-turbo", "Translate to Chinese: {input}")

    # 设置链条
    summarize_node.add_next(translate_node)

    # 执行链条
    # 创建提示模板
    prompt_template = PromptTemplate(
        template="What is the meaning of life?",
        input_variables=["input"]
    )

    # 准备输入数据
    prompt_data = {
        "prompt_template": prompt_template,
        "input": "What is the meaning of life?"
    }

    response = await service.get_response(prompt_data, ResponseModel)
    print("Chain Response:", response)


# 使用示例
async def chain_example_s():

    # 创建服务实例
    service = EnhancedLLMService(pool_size=3)

    # 创建执行器
    executor = ChainExecutor(service)

    # 创建节点
    summarize_node = ChainNode("gpt-4", "Summarize this: {input}")
    translate_node = ChainNode("gpt-3.5-turbo", "Translate to Chinese: {input}")

    # 设置链条
    summarize_node.add_next(translate_node)

    # 准备输入数据
    input_data = {
        "input": "The quick brown fox jumps over the lazy dog. This sentence is often used as a typing exercise because it contains all the letters of the English alphabet. It originated in the 19th century and has been widely used in typing classes, font design, and as a sample text in various applications. The sentence is known for its brevity while still containing every letter."
    }

    # 执行链
    results = await executor.execute(summarize_node, input_data, ResponseModel)

    # 输出结果
    print("原始输入:", input_data["input"])
    print("摘要结果:", results[0].response)  # 第一个结果是摘要
    print("翻译结果:", results[1].response)  # 第二个结果是翻译
    return results

if __name__ == "__main__":
    import asyncio
    #asyncio.run(example_usage())
    #asyncio.run(chain_example())
    asyncio.run(chain_example_s())