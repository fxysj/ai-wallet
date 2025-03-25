from abc import ABC,abstractmethod


from app.agents.schemas import AgentState
class StateStrategy(ABC):
    """状态策略基类"""
    @abstractmethod
    def get_prompt_next_action(self) -> dict:
        pass
