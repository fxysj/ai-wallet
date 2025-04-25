from app.agents.stateToolBindingFactory.StateStrategyFactory import StateStrategyFactory
from app.utuls.FieldCheckerUtil import FieldChecker


def handle_chain_result(result):
    """
    从链结果中提取 prompt_next_action，用于提示用户下一步行为
    """
    prompt_action = []

    try:
        # 先从 result 结构中取出 "state"
        state = FieldChecker.get_field_info(
            data=result.get("result", {}),
            field_name="state"
        )
        if state:
            # 通过工厂模式获取对应 state 的策略类
            strategy = StateStrategyFactory.get_strategy(state=state)
            prompt_action_dict = strategy.get_prompt_next_action()
            if prompt_action_dict:
                action = FieldChecker.get_field_info(
                    data=prompt_action_dict,
                    field_name="promptNextAction"
                )
                if action:
                    prompt_action = action
    except Exception as e:
        print(f"[handle_chain_result] error: {e}")
        prompt_action = []

    return prompt_action
