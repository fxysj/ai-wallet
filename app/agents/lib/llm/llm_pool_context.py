from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.extension.chain import ChainNode
from app.agents.lib.llm.extension.chain_executor import ParallelChainExecutor
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
# 基础信息和llm_pool功能类型
# Enhanced去封装了llm_service 可以添加事件监听装饰器的方式
# 变成了可以有事务处理 上下文对象 token计算 日志回调的能力
async def chain_example():
    service = EnhancedLLMService(pool_size=3)

    # 创建节点
    # summarize_node = ChainNode("gpt-4", "Summarize this: {input}")
    # translate_node = ChainNode("gpt-3.5-turbo", "Translate to Chinese: {input}")
    #
    # # 设置链条
    # summarize_node.add_next(translate_node)

    # 执行链条
    # 创建提示模板
    prompt_template = PromptTemplate(
        template="对 {input} 进行总结 言简意赅",
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
# 多个链路进行处理 并行处理的节点方式
async def chain_example_s():
    # 创建服务实例
    service = EnhancedLLMService(pool_size=3)

    # 创建执行器
    executor = ParallelChainExecutor(service)

    p = """
    Summarize this: {input}
    """
    pro = PromptTemplate(
        template=p,
        input_variables=["input"]
    )


    trao = "Translate to Chinese: {input}"
    pro2 = PromptTemplate(
        template=trao,
        input_variables=["input"]
    )
    # 创建节点
    summarize_node = ChainNode("gpt-4", pro, name="sum")
    translate_node = ChainNode("gpt-3.5-turbo", pro2, name="tra")

    # 准备输入数据
    input_data = {
        "input": "The quick brown fox jumps over the lazy dog. This sentence is often used as a typing exercise because it contains all the letters of the English alphabet. It originated in the 19th century and has been widely used in typing classes, font design, and as a sample text in various applications. The sentence is known for its brevity while still containing every letter."
    }

    # 执行链
    results = await executor.execute_parallel([summarize_node, translate_node], input_data, ResponseModel)

    # 输出结果

    print("原始输入:", input_data["input"])
    for r in results:
        print(r.get("result").response)
    return results


# 使用示例
async def parallel_chain_example():
    # 创建服务实例
    service = EnhancedLLMService(pool_size=3)

    # 创建执行器
    executor = ParallelChainExecutor(service)

    # 创建多个处理节点
    summarize_node = ChainNode(
        "gpt-4o",
        "Summarize this text in 2-3 sentences: {input}",
        name="Summarize"
    )

    translate_en_zh_node = ChainNode(
        "gpt-3.5-turbo",
        "Translate this text to Chinese: {input}",
        name="English-Chinese"
    )

    translate_en_fr_node = ChainNode(
        "gpt-3.5-turbo",
        "Translate this text to Chinese: {input}",
        name="English-Chinese"
    )

    sentiment_node = ChainNode(
        "gpt-3.5-turbo",
        "Analyze the sentiment of this text. Respond with only: positive, negative, or neutral: {input}",
        name="Sentiment"
    )
    # 准备输入数据
    input_data = {
        "input": "The new product launch exceeded all expectations. Sales were 50% higher than projected, and customer feedback has been overwhelmingly positive. The marketing team did an excellent job with the promotion, and the development team delivered a high-quality product on schedule. This success has boosted team morale and positioned us well for the next quarter."
    }
    print("1. 简单并行执行示例")
    print("-" * 50)

    # 并行执行多个节点
    parallel_results = await executor.execute_parallel(
        [summarize_node, translate_en_zh_node, sentiment_node],
        input_data,
        ResponseModel
    )

    # 输出每个节点的结果
    for result in parallel_results:
        node = result["node"]
        if result["status"] == "success":
            print(f"\n{node.name} 结果:")
            print(result["result"].response)
        else:
            print(f"\n{node.name} 失败: {result.get('error', 'Unknown error')}")




async def ahgghred():
    # 创建服务实例
    service = EnhancedLLMService(pool_size=3)

    # 创建执行器
    executor = ParallelChainExecutor(service)

    # 创建多个处理节点
    summarize_node = ChainNode(
        "gpt-4o",
        "Summarize this text in 2-3 sentences: {input}",
        name="Summarize"
    )

    translate_en_zh_node = ChainNode(
        "gpt-3.5-turbo",
        "Translate this text to Chinese: {input}",
        name="English-Chinese"
    )

    translate_en_fr_node = ChainNode(
        "gpt-3.5-turbo",
        "Translate this text to Chinese: {input}",
        name="English-Chinese"
    )

    sentiment_node = ChainNode(
        "gpt-3.5-turbo",
        "Analyze the sentiment of this text. Respond with only: positive, negative, or neutral: {input}",
        name="Sentiment"
    )
    # 准备输入数据
    input_data = {
        "input": "The new product launch exceeded all expectations. Sales were 50% higher than projected, and customer feedback has been overwhelmingly positive. The marketing team did an excellent job with the promotion, and the development team delivered a high-quality product on schedule. This success has boosted team morale and positioned us well for the next quarter."
    }
    # 定义聚合提示
    aggregation_prompt = """
          你收到了以下多个分析结果，请综合这些结果提供一个全面的报告。

          原始文本: {original_input}

          分析结果:
          {results}

          请提供一个综合报告，包含以下内容：
          1. 内容摘要
          2. 跨语言分析
          3. 情感评估
          4. 总体结论
          """
    # 并行执行后聚合
    aggregated_result = await executor.execute_parallel_with_aggregation(
        [summarize_node, translate_en_zh_node, sentiment_node],
        input_data,
        ResponseModel,
        aggregation_prompt
    )
    print(aggregated_result)

    # 输出聚合结果
    if aggregated_result["aggregation"]["status"] == "success":
        print("\n聚合结果:")
        print(aggregated_result["aggregation"]["result"].response)

    # print("\n\n3. 带有故障转移的执行示例")
    # print("-" * 50)
    #
    # # 创建一个故意会失败的节点
    # failing_node = ChainNode(
    #     "non-existent-model",  # 这会导致错误
    #     "This will fail: {input}",
    #     name="Failing-Node"
    # )
    #
    # # 执行带有故障转移的链条
    # fallback_result = await executor.execute_with_fallback(
    #     failing_node,
    #     [summarize_node, sentiment_node],  # 故障转移节点
    #     input_data,
    #     ResponseModel
    # )
    #
    # if fallback_result["status"] == "success":
    #     print(f"\n故障转移成功! 使用节点: {fallback_result['node'].name}")
    #     print(fallback_result["result"].response)
    # else:
    #     print("\n所有节点都失败了")
    # return parallel_results, aggregated_result, fallback_result
# 这个示例展示了三种并行处理模式：
# 1. 简单并行执行
# 同时执行多个不同的任务，然后单独处理每个结果：
# 摘要生成
# 英文到中文翻译
# 英文到法文翻译
# 情感分析
# 2. 并行执行后聚合
# 同时执行多个任务，然后将所有结果聚合为一个综合报告：
# 首先并行执行所有任务
# 收集所有成功的结果
# 将这些结果传递给一个聚合节点
# 生成一个综合报告
# 3. 带有故障转移的执行
# 实现高可用性处理，当主节点失败时自动尝试备用节点：
# 首先尝试主节点（在示例中，我们故意使用一个不存在的模型让它失败）
# 如果主节点失败，按顺序尝试备用节点
# 一旦有一个节点成功，就返回其结果

async def fallback():
    # 创建服务实例
    service = EnhancedLLMService(pool_size=3)

    # 创建执行器
    executor = ParallelChainExecutor(service)


    # 创建一个故意会失败的节点
    failing_node = ChainNode(
        "non-existent-model",  # 这会导致错误
        "This will fail: {input}",
        name="Failing-Node"
    )
    sentiment_node = ChainNode(
        "gpt-3.5-turbo",
        "Analyze the sentiment of this text. Respond with only: positive, negative, or neutral: {input}",
        name="Sentiment"
    )
    # 准备输入数据
    input_data = {
        "input": "The new product launch exceeded all expectations. Sales were 50% higher than projected, and customer feedback has been overwhelmingly positive. The marketing team did an excellent job with the promotion, and the development team delivered a high-quality product on schedule. This success has boosted team morale and positioned us well for the next quarter."
    }

    # 创建多个处理节点
    summarize_node = ChainNode(
        "gpt-4o",
        "Summarize this text in 2-3 sentences: {input}",
        name="Summarize"
    )

    # 执行带有故障转移的链条
    fallback_result = await executor.execute_with_fallback(
        failing_node,
        [summarize_node, sentiment_node],  # 故障转移节点
        input_data,
        ResponseModel
    )
    print(fallback_result)

    if fallback_result["status"] == "success":
        print(f"\n故障转移成功! 使用节点: {fallback_result['node'].name}")
        print(fallback_result["result"].response)
    else:
        print("\n所有节点都失败了")
if __name__ == "__main__":
    import asyncio

    asyncio.run(fallback())
    # asyncio.run(example_usage())
    # asyncio.run(chain_example())
    # asyncio.run(chain_example_s())
