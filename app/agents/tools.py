# 任务工具（如跨链查询等）
# 生成可视化图表
from langgraph.graph import StateGraph
from app.agents.schemas import *
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
def visualize_workflow(workflow: StateGraph):
    try:
        from graphviz import Digraph
        dot = Digraph()

        # 添加节点
        for node in workflow.nodes:
            dot.node(node.id, node.name)

        # 添加边
        for edge in workflow.edges:
            dot.edge(edge.source.id, edge.target.id)

        # 显示图表
        display(dot)
    except ImportError:
        print("请安装graphviz和pydot：pip install graphviz pydot")
    except Exception as e:
        print(f"无法生成图表: {str(e)}")
#更新AgentState sessions信息
def update_history(state: AgentState, intent_str: str)->AgentState:
    sessions = state.sessions.copy()
    if isinstance(sessions, list):
        sessions = {}
    if not isinstance(sessions, dict):
        sessions = {}

    history_list = sessions.get("history", [])
    new_history = [
        {"role": "user", "content": state.user_input},
        {"role": "assistant", "content": intent_str}
    ]
    history_list.extend(new_history)
    history_str = "\n".join(f"{msg['role']}: {msg['content']}" for msg in history_list)

    sessions["history"] = history_list
    updated_state = state.copy(update={
        "sessions": sessions,
        "history": history_str
    })
    return updated_state

# 对话历史管理工具
class ConversationManager:
    @staticmethod
    def update_history(state: AgentState, new_message: dict) -> AgentState:
        updated_messages = state.messages + [new_message]
        print(updated_messages)
        return state.copy(update={"messages": updated_messages[-5:]})

# 动态字段填充工具
class SchemaFillingTool:
    @staticmethod
    async def detect_missing_fields(schema_name: str, data: dict,llm) -> list:
        prompt = PromptTemplate(
            input_variables=["schema_name", "data"],
            template="""
            请列出{schema_name}中缺失的必填字段：
            {data}
            用逗号分隔，若无缺失返回"complete"
            """
        )
        chain = prompt | llm | StrOutputParser()
        response = await chain.ainvoke({
            "schema_name": schema_name,
            "data": json.dumps(data)
        })
        return response.strip().split(',') if response != "complete" else []

# 表单生成工具
class FormGenerator:
    @staticmethod
    def get_form_template(intent: Intention) -> str:
        form_templates = {
            Intention.send: """
            请填写以下转账信息：
            - 区块链索引（如 ethereum）: [chainIndex]
            - 源地址: [fromAddr]
            - 目标地址: [toAddr]
            - 转账数量: [txAmount]
            - 代币符号（如 ETH）: [tokenSymbol]
            - 代币合约地址: [tokenAddress]
            - 扩展JSON数据: [extJson]
            """,
            Intention.receive: """
            请填写以下接收信息：
            - 我的钱包地址: [myAddress]
            - 接收链（如 ethereum）: [myChain]
            """,
            Intention.swap: """
            请填写以下兑换信息：
            - 兑换来源资产: [from]
            - 兑换目标资产: [to]
            - 兑换数量: [amount]
            """,
            Intention.buy: """
            请填写以下购买信息：
            - 加密货币名称: [cryptoToken]
            - 法定货币名称: [fiatCurrency]
            - 购买金额: [amount]
            """,
            Intention.deep_research: """
            请填写以下研究请求：
            - 研究主题: [topic]
            """,
            Intention.account_analysis: """
            请填写以下分析请求：
            - 钱包地址: [walletAddress]
            - 区块链（可选）: [chain]
            """,
            Intention.newsletter: """
            请填写以下订阅信息：
            - 感兴趣的主题列表: [topics]
            - 时间范围（如 daily）: [timeframe]
            """
        }
        return form_templates.get(intent, "未找到对应的表单模板")

async def validate_attached_data(state: AgentState) -> AgentState:
    """
        验证用户提交的表单数据是否完整或符合预期：
        - 如果 attached_data 为空（{} 或 None），则返回对应意图的实体模板给前端，
          便于前端展示表单字段供用户填写。
        - 如果意图为 unclear，则直接标记 is_valid = True。
        - 否则使用 pydantic 进行验证，返回缺少字段提示。
        """
    print("=====进入校验阶段===========")
    if state.detected_intent in [Intention.unclear, None]:
        return state.copy(update={"is_valid": True})

    model_cls = {
        Intention.send: WalletTransactionSchema,
        Intention.receive: ReceiveInfoSchema,
        Intention.swap: SwapTransactionSchema,
        Intention.buy: BuyInfoSchema,
        Intention.deep_research: ResearchInfoSchema,
        Intention.account_analysis: AnalysisInfoSchema,
        Intention.newsletter: NewsletterInfoSchema
    }.get(state.detected_intent)

    if not model_cls:
        return state.copy(update={"is_valid": True})

    # 如果 attached_data 为空，则生成对应意图的实体模板
    if not state.attached_data or (isinstance(state.attached_data, dict) and len(state.attached_data) == 0):
        # 生成模板：所有必填字段以空字符串作为占位值
        default_entity_template = {field: "" for field in model_cls.__fields__.keys()}
        form_template = FormGenerator.get_form_template(state.detected_intent)
        print(form_template)
        return state.copy(update={
            "attached_data": default_entity_template,
            "is_valid": False,
            "task_result": f"请补充以下信息：\n{form_template}"
        })


    try:
        # 对传入的数据进行验证：支持 dict 或 pydantic 实例
        data = state.attached_data if isinstance(state.attached_data, dict) else state.attached_data.dict()
        model_cls(**data)
        return state.copy(update={"is_valid": True})
    except ValidationError as e:
        missing_fields = [
            error["loc"][0] for error in e.errors()
            if error["type"] == "value_error.missing"
        ]
        form_template = FormGenerator.get_form_template(state.detected_intent)
        return state.copy(update={
            "task_result": f"缺少必填字段: {', '.join(missing_fields)}\n请按照以下模板填写：\n{form_template}",
            "is_valid": False
        })


def get_nested_description(result, description_key="description", nested_result_key="result"):
    # 优先处理字符串类型
    if isinstance(result, str):
        return result

    # 处理嵌套结构
    if result is not None:
        nested_result = result.get(nested_result_key)
        if nested_result is not None:
            return nested_result.get(description_key)
    return None

import json
from typing import Optional, List, Dict, Any

def convert_to_openai_stream(result_dict: Dict[str, Any],
                                   tool_name: Optional[str] = None,
                                   tool_result: Optional[Dict[str, Any]] = None,
                                   custom_data: Optional[Dict[str, Any]] = None):
    # Extract description and other fields from the result_dict
    description = result_dict.get("data", {}).get("description", "")
    other_fields = {
        k: v for k, v in result_dict.get("data", {}).items()
        if k != "description"
    }

    # Inject custom data (if any)
    if custom_data:
        other_fields.update(custom_data)

    # Simulate tool call if tool_name and tool_result are provided
    tool_calls = []
    if tool_name and tool_result:
        # Construct a tool call following OpenAI's expected structure
        tool_calls.append({
            "id": "unique_tool_call_id",  # Unique tool call ID (can be generated dynamically)
            "name": tool_name,
            "arguments": tool_result,  # Assuming tool_result is a dict that represents the arguments
            "result": tool_result  # Return the same result for this example (this can be changed)
        })

    # First stage: Stream the description character by character
    for char in description:
        yield f"data: {json.dumps({
            'choices': [{
                'index': 0,
                'delta': {'content': char},
                'finish_reason': None
            }]
        })}\n\n"

    # Second stage: Send tool call information if provided
    if tool_calls:
        for tool_call in tool_calls:
            yield f"data: {json.dumps({
                'tool_calls': [{
                    'id': tool_call['id'],
                    'name': tool_call['name'],
                    'arguments': tool_call['arguments'],
                    'result': tool_call['result']
                }]
            })}\n\n"

    # Third stage: Send complete metadata (other fields and custom data)
    yield f"data: {json.dumps({
        'metadata': other_fields  # Other fields and custom data
    })}\n\n"

    # End marker to signify completion
    yield "data: [DONE]\n\n"

#返回
def GetWrapResponse(data:Any,history:[],system_response:str,missfield:str,description:str,is_completed:bool,detected_intent:str)-> dict:
    return {
            "data": data.dict() if isinstance(data, BaseModel) else data,  # 如果是 Pydantic 模型，使用 .dict(),
            "history": history,  # 历史信息
            "system_response": system_response,
            "missfield": missfield,
            "description": description,
            "is_completed":is_completed ,
            "detected_intent": detected_intent
        }

import random
#随机生成
#一个合理的代币合约地址应该是 以太坊（Ethereum）或其他区块链上的智能合约地址，通常是一个 42 位的十六进制字符串，以 0x 开头。例如：
# 示例
# 以太坊主网（Ethereum Mainnet）上 USDT（Tether） 的官方合约地址：
# 0xdAC17F958D2ee523a2206206994597C13D831ec7
def generate_random_address():
    return "0x" + "".join(random.choices("0123456789abcdef", k=40))


import os
from IPython.display import Image, display


def display_and_save_graph(app, filename="graph.png", output_dir="graphs"):
    """
    显示并保存 LangGraph 生成的 Mermaid 图。

    :param app: LangGraph 实例
    :param filename: 保存的文件名，默认为 "graph.png"
    :param output_dir: 存储图片的目录，默认为 "graphs"
    """
    try:
        # 生成图像
        img_data = app.get_graph().draw_mermaid_png()

        # 显示图片
        display(Image(img_data))

        # 保存图片
        os.makedirs(output_dir, exist_ok=True)
        graph_path = os.path.join(output_dir, filename)

        with open(graph_path, "wb") as f:
            f.write(img_data)

        print(f"Graph image saved at: {graph_path}")

    except Exception as e:
        print(f"Failed to generate graph: {e}")

# 调用示例：
# display_and_save_graph(app)

# 调用示例：
# save_graph_image(app)


import jwt


import jwt
from fastapi import Request
from typing import Dict


def get_user_id_from_authorization(request: Request) -> Dict[str, str]:
    authorization = request.headers.get("Authorization")
    if not authorization:
        return {"user_id": ""}
    try:
        token = authorization.split(" ")[-1]
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("id")
        return {"user_id": user_id if user_id else ""}
    except:
        return {"user_id": ""}

if __name__ == '__main__':
    # Example usage:
    # jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDQzNjczMzAsImlhdCI6MTc0MTc3NTMzMCwiRXZtQWRkcmVzcyI6IjB4ZUI3YWI2ZmI4NjJiMzQ5YzhmMDM5MTI0YTBmM0U1RWU5MzMzMGZjOCIsIlNvbGFuYUFkZHJlc3MiOiI2Z21YWGVvb2VETEN0UXEyMzRlTVB5RzY4V2dtSE11ODY0Nzl5S2Rlb1UxUiIsIlRyb25BZGRyZXNzIjoiVENjWEw1Qnh6V1VNdndKcnljcUVqNFVvNE13dU1qeDlzcyIsImlkIjoxMH0.MDhDh1ezDe5IEwdduDABLzRtBzxrxcY8GP__ihKpxR0"
    result_dict = {
        "data": {
            "description": "This is a description.",
            "indent":"send",
            "state":"ACTION",
            "form": {
                "chaindex":"111"
            },
            "missField":[],
            "DxTranctionDetail":{},
        }
    }

    tool_name = "get_current_weather"
    tool_result = {
        "temperature": "22°C",
        "location": "London"
    }

    custom_data = {
        "role":"system",
        "content":"",
        "Success": "true",
        "message":"ok",
        "propmentAction":[],
    }

    for data in convert_to_openai_stream(result_dict, tool_name=tool_name, tool_result=tool_result,
                                               custom_data=custom_data):
        print(data)





