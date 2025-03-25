from app.agents.stateToolBindingFactory.StateStrategyFactory import StateStrategyFactory

def process_state(state: str):
    """根据状态选择策略，并返回相应的 promptNextAction"""
    try:
        strategy = StateStrategyFactory.get_strategy(state)
        return strategy.get_prompt_next_action()
    except ValueError as e:
        raise e
if __name__ == '__main__':
    # 示例调用
    try:
        state = "READY_TO_SIGN_TRANSACTION"
        result = process_state(state)
        print(result)  # 输出：{"promptNextAction": ["PASTE_FROM_CLIPBOARD", "PASTE_FROM_ADDRESSBOOK", "SCAN_QR_CODE"]}
    except ValueError as e:
        print(e)



