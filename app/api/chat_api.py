import logging
import time

from langchain_core.messages import HumanMessage
from langchain_core.tracers import LangChainTracer
from langsmith import Client

from  app.agents.lib.llm.llm import  LLMFactory
from app.agents.tasks.analysis_task import parse_complex_intent
from ..agents.lib.redisManger.redisManager import RedisDictManager
from ..agents.lib.session.TranSession import TransactionSystem
from ..agents.response.Response import SystemResponse
from ..agents.stateToolBindingFactory.StateStrategyFactory import StateStrategyFactory
from ..agents.tasks.user_langguage import userLangGuageAnaysic
from ..agents.tasks.buy_task import buy_task
from ..agents.tasks.deep_accunt_analysis import analysis_task
from ..agents.tasks.deep_search_task import research_task
from ..agents.tasks.handle_unclear import unclear_task
from ..agents.tasks.news_task import news_task
from ..agents.tasks.receive_task import receive_task
from ..agents.tasks.route import route_task
from ..agents.tasks.send_task import send_task
from ..agents.tasks.swap_task import swap_task
from fastapi import APIRouter
from langgraph.graph import END
from app.agents.tools import *
from app.config import settings
from app.agents.lib.redisManger.redisManager import redis_dict_manager
from fastapi.responses import StreamingResponse
# from app.agents.lib.session.sessionManager import  dict_manager
# from langgraph.checkpoint.memory import MemorySaver
# 配置 LangSmith 追踪器
# from langsmith.wrappers import wrap_openai
# ------------------------------------------------------------------------------
# 日志与应用初始化
# ------------------------------------------------------------------------------
from ..utuls.FieldCheckerUtil import FieldChecker
from ..utuls.Messages import Session

# 实例化 RedisDictManager
from ..utuls.prompt import convert_to_openai_messages

redis_dict_manager = redis_dict_manager
#实例化日志模块
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#初始化路由
router = APIRouter()
#初始化大模型
llm = LLMFactory.getOpenAI(open_key=settings.OPENAI_API_KEY,url=settings.OPENAI_API_BASE_URL)
#初始化构建Session内存的模式
# 构建工作流

# 初始化 LangSmith 客户端（自动读取环境变量）
# client = Client()
# # 初始化跟踪器
# tracer = LangChainTracer(client=client)
workflow = StateGraph(AgentState)

workflow.add_node("user_langguage",userLangGuageAnaysic) #分析用户的语言类型
workflow.add_node("intent_parser", parse_complex_intent) #意图智能体
workflow.add_node("handle_send", send_task) #转账智能体
workflow.add_node("handle_receive", receive_task) #收款智能体
workflow.add_node("handle_swap", swap_task) #兑换跨链智能体
workflow.add_node("handle_buy", buy_task) #购买法币智能体
workflow.add_node("handle_research", research_task) #深度搜索智能体
workflow.add_node("handle_analysis", analysis_task) #账号深度分析智能体
workflow.add_node("handle_news", news_task) #新闻投资资讯智能体
workflow.add_node("handle_unclear",unclear_task) #没有完成的智能体
workflow.add_edge("user_langguage","intent_parser") #设置边 用户行为
#条件边
workflow.add_conditional_edges(
    "intent_parser",
    route_task,
    {
        Intention.send.value: "handle_send",
        Intention.receive.value: "handle_receive",
        Intention.swap.value: "handle_swap",
        Intention.buy.value: "handle_buy",
        Intention.deep_research.value: "handle_research",
        Intention.account_analysis.value: "handle_analysis",
        Intention.newsletter.value: "handle_news",
        Intention.unclear.value: "handle_unclear",
    }
)
for node in [
    "handle_send", "handle_receive", "handle_swap",
    "handle_buy", "handle_research", "handle_analysis",
    "handle_news", "handle_unclear"
]:
    workflow.add_edge(node, END)

workflow.set_entry_point("user_langguage")

# 添加追踪器
app = workflow.compile()

#保存对应的流图片
display_and_save_graph(app=app,filename="graph.png",output_dir="graphs")

# 生成流式响应的生成器函数
async def stream_response(result: Dict):
    try:
        # Convert the result to JSON and then encode it
        json_data = json.dumps(result).encode('utf-8')

        # Use a chunk size for streaming. This avoids processing the entire payload in memory at once.
        chunk_size = 1024  # Adjust depending on your use case (e.g., 1KB per chunk)

        # Yield the chunks of JSON data
        for i in range(0, len(json_data), chunk_size):
            yield json_data[i:i + chunk_size]

    except Exception as e:
        logger.error(f"Error during stream response: {str(e)}")
        # Instead of sending a fixed error message, it’s better to stream the error too
        yield b"Error processing request"





def process_tool_calls(stream,available_tools):
    draft_tool_calls = []
    draft_tool_calls_index = -1

    # 处理流的每个chunk
    for chunk in stream:
        # Log the structure of the chunk for debugging
        print(json.dumps(chunk, indent=2))  # This will print the chunk structure

        # Check if 'choices' exist in the chunk
        if hasattr(chunk, 'choices'):
            for choice in chunk.choices:
                if choice.finish_reason == "stop":
                    continue

                elif choice.finish_reason == "tool_calls":
                    # 处理工具调用
                    for tool_call in draft_tool_calls:
                        # 模拟工具调用并返回状态
                        tool_result = available_tools[tool_call["name"]](
                            **json.loads(tool_call["arguments"]))
                        # 更新图的状态
                        #graph.update_state(tool_call["id"], tool_result)

                        yield 'a:{{"toolCallId":"{id}","toolName":"{name}","args":{args},"result":{result}}}\n'.format(
                            id=tool_call["id"],
                            name=tool_call["name"],
                            args=tool_call["arguments"],
                            result=json.dumps(tool_result))

                    # 返回图的完整状态值
                    yield f'graph:{json.dumps(graph.get_full_state())}\n'

                elif choice.delta.tool_calls:
                    # 处理新的工具调用
                    for tool_call in choice.delta.tool_calls:
                        id = tool_call.id
                        name = tool_call.function.name
                        arguments = tool_call.function.arguments

                        if id is not None:
                            draft_tool_calls_index += 1
                            draft_tool_calls.append(
                                {"id": id, "name": name, "arguments": ""})
                        else:
                            draft_tool_calls[draft_tool_calls_index]["arguments"] += arguments

                else:
                    # 输出文本内容
                    yield '0:{text}\n'.format(text=json.dumps(choice.delta.content))
        else:
            # If 'choices' attribute doesn't exist, log this
            print(f"Chunk does not have 'choices': {json.dumps(chunk, indent=2)}")

        if chunk.choices == []:
            # 输出消耗的token信息
            usage = chunk.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens

            yield 'e:{{"finishReason":"{reason}","usage":{{"promptTokens":{prompt},"completionTokens":{completion}}},"isContinued":false}}\n'.format(
                reason="tool-calls" if len(draft_tool_calls) > 0 else "stop",
                prompt=prompt_tokens,
                completion=completion_tokens
            )


def process_stream(stream, available_tools):
    draft_tool_calls = []
    draft_tool_calls_index = -1

    for chunk in stream:
        for choice in chunk.choices:
            if choice.finish_reason == "stop":
                continue

            elif choice.finish_reason == "tool_calls":
                for tool_call in draft_tool_calls:
                    yield '9:{{"toolCallId":"{id}","toolName":"{name}","args":{args}}}\n'.format(
                        id=tool_call["id"],
                        name=tool_call["name"],
                        args=tool_call["arguments"])

                for tool_call in draft_tool_calls:
                    tool_result = available_tools[tool_call["name"]](
                        **json.loads(tool_call["arguments"]))

                    yield 'a:{{"toolCallId":"{id}","toolName":"{name}","args":{args},"result":{result}}}\n'.format(
                        id=tool_call["id"],
                        name=tool_call["name"],
                        args=tool_call["arguments"],
                        result=json.dumps(tool_result))

            elif choice.delta.tool_calls:
                for tool_call in choice.delta.tool_calls:
                    id = tool_call.id
                    name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    if id is not None:
                        draft_tool_calls_index += 1
                        draft_tool_calls.append(
                            {"id": id, "name": name, "arguments": ""})
                    else:
                        draft_tool_calls[draft_tool_calls_index]["arguments"] += arguments

            else:
                yield '0:{text}\n'.format(text=json.dumps(choice.delta.content))

        if not chunk.choices:
            usage = chunk.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens

            yield 'e:{{"finishReason":"{reason}","usage":{{"promptTokens":{prompt},"completionTokens":{completion}}},"isContinued":false}}\n'.format(
                reason="tool-calls" if draft_tool_calls else "stop",
                prompt=prompt_tokens,
                completion=completion_tokens
            )


# ------------------------------------------------------------------------------
# API 接口
# ------------------------------------------------------------------------------
@router.get("/start")
async def create_session() -> dict:
    """
    创建新会话接口：
      - 初始化交易数据
      - 调用链生成系统响应（system_response），返回表单填充提示
    """
    try:
        session = TransactionSystem.new_session()
        session[
            "system_response"] = "您好，目前转账信息还不完整，您需要补充转账地址、来源地址（必须以 '0x' 开头）、转账金额（需大于0）、数字货币类型（仅支持 BTC、ETH、USDT）以及区块链网络（仅支持 ETH、BSC、TRX）"
        #dict_manager.add(session["session_id"],session)
        redis_dict_manager.add(session["session_id"],session) #替换为Redis
        return BaseResponse.success(session)
    except Exception as e:
        logger.error(f"会话创建失败: {str(e)}")
        return BaseResponse.error(500, "服务初始化失败")


@router.get("/test",summary="测试接口")
async def test(request:Request):
    return BaseResponse.success(request)

# API端点
@router.post("/chat",summary="大模型统一入口")
async def analyze_request(request: Request):
    """
       处理用户请求接口：
         - 根据会话ID找到对应会话
         - 调用链处理当前输入，获取完整表单信息与补充提示
         - 合并数据并更新会话历史
       """
    try:
        request_data = await request.json()
        #从头部获取 id信息
        user_id_info = get_user_id_from_authorization(request)
        user_id = user_id_info["user_id"]
        user_id = str(user_id)

        session_id = user_id
        messages = request_data.get("messages")
        print(session_id)
        if not session_id:
            return SystemResponse.error_with_message(
                message="请先进行授权登录钱包",
            )


        session = redis_dict_manager.get(session_id)
        #如果没有找到则返回一个空的信息
        if session == None:
            user_seession = {"history":[]}
            redis_dict_manager.add(user_id,user_seession)


        user_input_object = Session.get_last_user_message(request_data)

        current_data = user_input_object.data
        user_attached_data = current_data

        # 组装最近的对话历史（取最新5条记录）
        history = Session.get_recent_history(request_data,10)



        initial_state = AgentState(
            user_input=user_input_object.content,#用户输入信息
            attached_data=user_attached_data,#用户保存的数据信息
            session_id=session_id,#会话信息
            history=history, #历史上下文信息
            messages=messages,#历史信息
            langguage=settings.LanGuage,#语言配置
            isAsync=settings.ISLangGuageAynsNIS,#是否进行配置
            detected_intent=Intention.unclear#默认不知道

        )
        result = await app.ainvoke(initial_state)

        print("DEBUG - result 类型:", type(result))

        print(user_input_object)
        # 更新对话历史
        session["history"].extend([
            {"role": "user", "content": user_input_object.content,"data":user_input_object.data},
            {"role": "system", "content": get_nested_description(result),"data":result}
        ])
        #更新session中的数据
        #session["data"] = get_nested_description(result,"data","result")
        #dict_manager.update(session_id,session)
        #下面最好使用异步的方式进行构建
        redis_dict_manager.update(session_id,session)

        print(result)

        state = FieldChecker.get_field_info(
            data=result["result"],
            field_name="state"
        )
        prom_action = []
        if state:
            try:
                strategy = StateStrategyFactory.get_strategy(state=state)
                prom_action_dict = strategy.get_prompt_next_action()
                if prom_action_dict:
                    action = FieldChecker.get_field_info(
                        data=prom_action_dict,
                        field_name="promptNextAction"
                    )
                    if action :
                        prom_action = action
            except ValueError as e:
                print(e)

                # 将结果包装为流式响应

        response_data = SystemResponse.success(
            prompt_next_action=prom_action,
            data=result["result"],
            content=get_nested_description(result)
        )

        # response =  StreamingResponse(
        #     convert_to_openai_stream(response_data.to_dict()),
        #     media_type="text/event-stream",
        #     headers={
        #         "Cache-Control": "no-cache",
        #         "Connection": "keep-alive"
        #     })
        # response.headers['x-vercel-ai-data-stream'] = 'v1'
        return response_data
    except KeyError:
        response_data= SystemResponse.errorWrap(
            data=result["result"],
            message="系统内部错误",
            prompt_next_action=prom_action,
        )
        # return StreamingResponse(
        # convert_to_openai_stream(response_data.to_dict()),
        # media_type="text/event-stream",
        # headers={
        #     "Cache-Control": "no-cache",
        #     "Connection": "keep-alive"
        # })
        return response_data
    except ValidationError as e:
        response_data =  SystemResponse.errorWrap(
            data=result["result"],
            message="系统内部错误",
            prompt_next_action=prom_action,
        )
        # return StreamingResponse(
        # convert_to_openai_stream(response_data.to_dict()),
        # media_type="text/event-stream",
        # headers={
        #     "Cache-Control": "no-cache",
        #     "Connection": "keep-alive"
        # })
        return response_data
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        print(e)
        response_data= SystemResponse.errorWrap(
            data=result["result"],
            message="系统内部错误",
            prompt_next_action=prom_action,
        )
        return response_data
        # return StreamingResponse(stream_response(response_data.to_dict()), media_type="application/json")
    except ValueError as e:
        logger.error(f"Processing failed: {str(e)}")
        print(e)
        response_data =  SystemResponse.errorWrap(
            data=result["result"],
            message="系统内部错误",
            prompt_next_action=prom_action,
        )
        return response_data
        # return StreamingResponse(stream_response(response_data), media_type="application/json")