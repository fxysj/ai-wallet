from app.agents.stateToolBindingFactory.StateStragtegy import StateStrategy
from app.config import settings, CONFIG


class ReadyToSignTransactionStrategy(StateStrategy):
    """处理 READY_TO_SIGN_TRANSACTION 状态的策略"""

    def get_prompt_next_action(self) -> dict:
        return CONFIG.get("READY_TO_SIGN_TRANSACTION", {})


class WaitingForConfirmationStrategy(StateStrategy):
    """处理 WAITING_FOR_CONFIRMATION 状态的策略"""

    def get_prompt_next_action(self) -> dict:
        return CONFIG.get("WAITING_FOR_CONFIRMATION", {})


class RANSACTIONFAILEDStrategy(StateStrategy):
        """处理 RANSACTION_FAILED 状态的策略"""

        def get_prompt_next_action(self) -> dict:
            return CONFIG.get("RANSACTION_FAILED", {})

class  REQUESTMOREINFOStrategy(StateStrategy):
     """处理 REQUEST_MORE_INFO 状态的策略"""

     def get_prompt_next_action(self) -> dict:
         return CONFIG.get("REQUEST_MORE_INFO", {})
