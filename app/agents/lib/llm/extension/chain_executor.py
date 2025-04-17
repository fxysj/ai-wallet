import asyncio
from typing import Type, Dict, Any, List

from pydantic import BaseModel

from app.agents.lib.llm.extension.chain import ChainNode
from app.agents.lib.llm.llm_pool import ResponseModel


class ChainExecutor:
    def __init__(self, llm_service):
        self.llm_service = llm_service

    async def execute(self, start_node: ChainNode, input_data: Dict[str, Any],
                      response_model: Type[BaseModel], context=None):
        """执行链式调用"""
        results = []
        current_input = input_data

        # 执行当前节点
        formatted_prompt = start_node.prompt_template.format(**current_input)
        prompt_data = {
            "input": formatted_prompt,
            "model": start_node.model
        }

        # 调用LLM服务
        result = await self.llm_service.get_response(
            {"prompt_template": start_node.prompt_template, **current_input},
            response_model
        )

        results.append(result)

        # 准备下一个节点的输入
        if hasattr(result, 'response'):
            next_input = {"input": result.response}
        else:
            next_input = {"input": str(result)}

        # 执行后续节点
        for next_node in start_node.next_nodes:
            if next_node.condition is None or next_node.condition(result):
                next_results = await self.execute(
                    next_node,
                    next_input,
                    response_model,
                    context
                )
                results.extend(next_results)

        return results

# 添加并行处理
async def execute_parallel(self, nodes: List[ChainNode], input_data):
    tasks = [self.execute(node, input_data, ResponseModel) for node in nodes]
    return await asyncio.gather(*tasks)

# 添加错误处理
async def execute_with_fallback(self, primary_node, fallback_node, input_data):
    try:
        return await self.execute(primary_node, input_data, ResponseModel)
    except Exception as e:
        print(f"Primary node failed: {e}, trying fallback")
        return await self.execute(fallback_node, input_data, ResponseModel)
