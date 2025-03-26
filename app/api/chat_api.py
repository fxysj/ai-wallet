import logging

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
redis_dict_manager = redis_dict_manager
#实例化日志模块
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.info("Received a request to the root endpoint")
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
@router.post("/start")
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


# API端点
@router.post("/chat",summary="大模型统一入口")
async def analyze_request(request: dict):
    """
       处理用户请求接口：
         - 根据会话ID找到对应会话
         - 调用链处理当前输入，获取完整表单信息与补充提示
         - 合并数据并更新会话历史
       """
    try:
        session_id = request.get("session_id")
        messages = request.get("messages")
        if not session_id or redis_dict_manager.get(session_id) is None:
            return SystemResponse.error_with_message(
                message="请先进行授权登录钱包",
            )

        session = redis_dict_manager.get(session_id)

        user_input_object = Session.get_last_user_message(request)

        current_data = user_input_object.data
        user_attached_data = current_data

        # 组装最近的对话历史（取最新5条记录）
        history = Session.get_recent_history(request,10)



        initial_state = AgentState(
            user_input=user_input_object.content,#用户输入信息
            attached_data=user_attached_data,#用户保存的数据信息
            session_id=session_id,#会话信息
            history=history, #历史上下文信息
            messages=messages,#历史信息
            detected_intent=Intention.unclear#默认不知道
        )
        result = await app.ainvoke(initial_state)

        print("DEBUG - result 类型:", type(result))
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




        return SystemResponse.success(
            prompt_next_action=prom_action,
            data=result["result"],
            content=get_nested_description(result)
            )
    except KeyError:
        return SystemResponse.errorWrap(
            data=result["result"],
            message="系统内部错误",
            prompt_next_action=prom_action,
        )
    except ValidationError as e:
        return SystemResponse.errorWrap(
            data=result["result"],
            message="系统内部错误",
            prompt_next_action=prom_action,
        )
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        print(e)
        return SystemResponse.errorWrap(
            data=result["result"],
            message="系统内部错误",
            prompt_next_action=prom_action,
        )
    except ValueError as e:
        logger.error(f"Processing failed: {str(e)}")
        print(e)
        return SystemResponse.errorWrap(
            data=result["result"],
            message="系统内部错误",
            prompt_next_action=prom_action,
        )