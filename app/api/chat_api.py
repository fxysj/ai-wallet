import logging
import uuid
from json import JSONDecodeError
from  app.agents.lib.llm.llm import  LLMFactory
from app.agents.tasks.analysis_task import parse_complex_intent
from .exceptions.exceptions import BusinessException
from app.agents.utils import chain_data_util
from ..agents.form.form import TaskState
from ..agents.lib.aiNodeJsSDk.tools.AgentStateResponseWrape import stream_text_agent_state, generate_chat_responses, \
    stream_text_agent_state_transfor
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
# ------------------------------------------------------------------------------
# API 接口
# ------------------------------------------------------------------------------
@router.get("/test",summary="测试接口")
async def test(request:Request):
    initial_state = AgentState(
        user_input="我想转账",  # 用户输入信息
        attached_data={"indent":Intention.unclear.value},  # 用户保存的数据信息
        session_id="sdsadsadsad",  # 会话信息
        history="",  # 历史上下文信息
        chain_data={},  # 链数据
        messages=[],  # 历史信息
        langguage=settings.LanGuage,  # 语言配置
        isAsync=settings.ISLangGuageAynsNIS,  # 是否进行配置
        detected_intent=Intention.unclear,  # 默认不知道
        thinking_info=""
    )
    result = await app.ainvoke(initial_state)
    print("DEBUG - result 类型:", type(result))
    print("result:", result)
    # ✅ 将其挂载到 request 上，供中间件后续使用
    request.state.agent_state = result
    return BaseResponse.success(result)

#测试业务异常
@router.get("/ex")
async def test_error():
    raise BusinessException(code=1001,msg="测试业务异常")


@router.get("/parser")
async def test_parser():
    from langchain_core.exceptions import OutputParserException
    raise OutputParserException("这是一个输出解析错误")


@router.post("/research/result")
async def getResarchResult(request:Request):
        projectId = ""
        request_data = await request.json()
        user_input_object = Session.get_last_user_message(request_data)
        id = request_data.get("id")
        session_id = request_data.get("session_id")
        if id:
            session_id = id

        data = user_input_object.data
        print(data)
        if data:
            if data.get("form"):
                selectedProject = data.get("form").get("selectedProject")
                if selectedProject:
                    projectId = selectedProject.get("id")

        key = f"research:{session_id}:projectId:{data.get('form', {}).get('selectedProject', {}).get('id')}"
        defultData = {"progress": 0, "message": "deepSearchProjectData...", "data": {}}
        res = redis_dict_manager.get(key)
        if not res:
            return defultData
        return res





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
        # user_id_info = get_user_id_from_authorization(request)
        # user_id = user_id_info["user_id"]
        # user_id = str(user_id)

        session_id = request_data.get("session_id")
        id= request_data.get("id")
        messages = request_data.get("messages")
        print(session_id)
        if id:
            session_id  = id
        if not session_id:
            return SystemResponse.error_with_message(
                message="请先进行授权登录钱包",
            )


        session = redis_dict_manager.get(session_id)
        print("--------session-------------")
        print(session)
        print("---------id:"+id)
        #如果没有找到则返回一个空的信息
        if session == None:
            user_seession = {"history":[],"data":{},"session_id": str(uuid.uuid4())}
            redis_dict_manager.add(session_id,user_seession)


        user_input_object = Session.get_last_user_message(request_data)

        current_data = user_input_object.data
        user_attached_data = current_data

        # 组装最近的对话历史（取最新5条记录）
        history = Session.get_recent_history(request_data,10)
        chain_data = chain_data_util.DEFAULT_CHAIN_DATA

        # 在调用 LangChain 完成后，记录思考信息
        thinking_info = "模型正在进行思考..."  # 你可以在这里插入模型推理过程中的中间信息

        initial_state = AgentState(
            user_input=user_input_object.content,#用户输入信息
            attached_data=user_attached_data,#用户保存的数据信息
            session_id=session_id,#会话信息
            history=history, #历史上下文信息
            chain_data=chain_data,#链数据
            messages=messages,#历史信息
            langguage=settings.LanGuage,#语言配置
            isAsync=settings.ISLangGuageAynsNIS,#是否进行配置
            detected_intent=Intention.unclear,#默认不知道
            thinking_info=thinking_info
        )

        result = await app.ainvoke(initial_state)
        print("DEBUG - result 类型:", type(result))
        print("result:",result)
        # ✅ 将其挂载到 request 上，供中间件后续使用
        request.state.agent_state = result
        # 确保 session 已初始化，防止为 None 的错误
        if session is None:
            session = {}

        # 如果 session["history"] 为 None，则初始化为一个空列表
        # 确保 session["history"] 不是 None
        if session.get("history") is None:
            session["history"] = []

        session["history"].extend([
            {"role": "user", "content": user_input_object.content,"data":user_input_object.data},
            {"role": "system", "content": get_nested_description(result),"data":result}
        ])
        #更新session中的数据
        #session["data"] = get_nested_description(result,"data","result")
        #dict_manager.update(session_id,session)
        #下面最好使用异步的方式进行构建
        redis_dict_manager.update(session_id,session)

        state = FieldChecker.get_field_info(
            data=result.get("result", {}),  # 如果 result["result"] 不存在，返回空字典 {}
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


        print(prom_action)

        response_data = SystemResponse.success(
            prompt_next_action=prom_action,
            data=result.get("result", {}),  # 如果 result["result"] 不存在，返回空字典 {}
            message="ok",
            content=get_nested_description(result)
        )
        res = stream_text_agent_state_transfor(content=get_nested_description(result),
                                data=response_data.to_dict()
                                )

        response =  StreamingResponse(res,media_type="text/event-stream")
        response.headers["x-vercel-ai-data-stream"] = "v1"
        #return response_data
        return response
    except KeyError:
        response_data= SystemResponse.errorWrap(
            data=result.get("result", {}),
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
            data=result.get("result", {}),
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
            data=result.get("result", {}),
            message="系统内部错误",
            prompt_next_action=prom_action,
        )
        res = stream_text_agent_state_transfor("请稍后重试",response_data.to_dict())
        response = StreamingResponse(res,media_type="text/event-stream")
        response.headers["x-vercel-ai-data-stream"] = "v1"
        return  response
        #return response_data
        #  return StreamingResponse(stream_text_agent_state(), media_type="application/json")
    except ValueError as e:
        logger.error(f"Processing failed: {str(e)}")
        print(e)
        response_data =  SystemResponse.errorWrap(
            data=result.get("result", {}),
            message="系统内部错误",
            prompt_next_action=prom_action,
        )
        return response_data
        # return StreamingResponse(stream_response(response_data), media_type="application/json")
    except JSONDecodeError as e:
        response_data = SystemResponse.errorWrap(
            data=result.get("result", {}),
            message="Please try again!",
            prompt_next_action=prom_action,
        )
        res = stream_text_agent_state_transfor("Please try again!", response_data.to_dict())
        response = StreamingResponse(res,media_type="text/event-stream")
        response.headers["x-vercel-ai-data-stream"] = "v1"
        return response
