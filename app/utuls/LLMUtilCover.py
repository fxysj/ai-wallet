from app.agents.schemas import AgentState, Intention, WalletTransactionSchema
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)
#本工具库用来将大模型返回的数据字典转为 LangGraph公共的状态对象
#exmple :
 # 例子: result = {}
  # convert_dict_to_agent_state(result)
def convert_dict_to_agent_state(result_dict):
    try:
        # 确保 attached_data 是字典形式
        attached_data = result_dict["attached_data"]
        if hasattr(attached_data, 'dict'):
            attached_data = attached_data.dict()

        return AgentState(
            messages=result_dict["messages"],
            latest_input=result_dict["latest_input"],
            attached_data=attached_data,
            detected_intent=result_dict["detected_intent"],
            task_result=result_dict["task_result"],
            is_valid=result_dict["is_valid"],
            is_signed=result_dict["is_signed"],
            is_completed=result_dict["is_completed"]
        )
    except KeyError as e:
        logger.error(f"字典缺少必要的键: {e}")
        raise HTTPException(400, f"字典缺少必要的键: {e}")
    except ValueError as e:
        logger.error(f"值错误: {e}")
        raise HTTPException(400, f"值错误: {e}")
    except Exception as e:
        logger.error(f"转换失败: {e}")
        raise HTTPException(500, "状态转换失败")

#根据 AgentState 返回不同的响应请求进行包装
#进行装饰器装饰
def converAgentStateResult(resultAgent:AgentState):
    return resultAgent