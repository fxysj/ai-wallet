import asyncio
from typing import Type, Dict, Any, List

from pydantic import BaseModel

from app.agents.lib.llm.extension.chain import ChainNode
from app.agents.lib.llm.llm_pool import ResponseModel


class ParallelChainExecutor:
    def __init__(self, llm_service):
        self.llm_service = llm_service

    async def execute_node(self, node: ChainNode, input_data: Dict[str, Any],
                           response_model: Type[BaseModel]):
        """执行单个节点"""
        try:
            formatted_prompt = node.prompt_template.format(**input_data)
            prompt_data = {
                "prompt_template": node.prompt_template,
                **input_data
            }

            result = await self.llm_service.get_response(prompt_data, response_model)
            print(f"节点 {node.name} 执行完成")
            return {"node": node, "result": result, "status": "success"}
        except Exception as e:
            print(f"节点 {node.name} 执行失败: {str(e)}")
            return {"node": node, "result": None, "status": "error", "error": str(e)}

    # 添加并行处理
    async def execute_parallel(self, nodes: List[ChainNode], input_data: Dict[str, Any],response_model: Type[BaseModel]):
        tasks = [self.execute_node(node, input_data, response_model) for node in nodes]
        """并行执行多个节点"""
        return await asyncio.gather(*tasks)


    async def execute_parallel_with_aggregation(self, nodes: List[ChainNode],
                                            input_data: Dict[str, Any],
                                            response_model: Type[BaseModel],
                                            aggregation_prompt: str):
        """并行执行多个节点，然后聚合结果"""
        # 并行执行所有节点
        node_results = await self.execute_parallel(nodes, input_data, response_model)

        # 提取所有成功的结果
        successful_results = [r["result"].response for r in node_results if r["status"] == "success"]

        # 如果没有成功的结果，返回错误
        if not successful_results:
            return {"status": "error", "message": "All parallel nodes failed"}

        # 准备聚合节点的输入
        aggregate_input = {
            "results": "\n\n".join([f"结果 {i + 1}: {result}" for i, result in enumerate(successful_results)]),
            "original_input": input_data.get("input", "")
        }
        # 创建聚合节点
        aggregation_node = ChainNode(
            "gpt-4o",
            aggregation_prompt,
            name="Aggregation-Node"
        )

        # 执行聚合
        aggregation_result = await self.execute_node(
            aggregation_node,
            aggregate_input,
            response_model
        )


        return {
            "individual_results": node_results,
            "aggregation": aggregation_result
        }


    # 添加错误处理
    async def execute_with_fallback(self, main_node: ChainNode,
                                   fallback_nodes: List[ChainNode],
                                   input_data: Dict[str, Any],
                                   response_model: Type[BaseModel]):
        """执行带有故障转移的链条"""
        try:
            # 尝试主节点
            main_result = await self.execute_node(main_node, input_data, response_model)
            if main_result["status"] == "success":
                return main_result
        except Exception as e:
            print(f"主节点失败: {e}")

            # 如果主节点失败，尝试故障转移节点
            for fallback_node in fallback_nodes:
                try:
                    fallback_result = await self.execute_node(fallback_node, input_data, response_model)
                    if fallback_result["status"] == "success":
                        return fallback_result
                except Exception as e:
                    print(f"故障转移节点 {fallback_node.name} 失败: {e}")

            # 如果所有节点都失败，返回错误
            return {"status": "error", "message": "All nodes (main and fallbacks) failed"}
