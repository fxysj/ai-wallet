from app.agents.stateToolBindingFactory import ReadyToSignTransactionStrategy
from app.agents.stateToolBindingFactory.ReadyToSignTransactionStrategy import WaitingForConfirmationStrategy
from app.agents.stateToolBindingFactory.StateStragtegy import StateStrategy
from importlib import import_module

class StateStrategyFactory:
    """策略工厂类，根据 state 返回对应的策略类"""

    strategies = {
        "READY_TO_SIGN_TRANSACTION": "app.agents.stateToolBindingFactory.ReadyToSignTransactionStrategy.ReadyToSignTransactionStrategy",
        "WAITING_FOR_CONFIRMATION": "app.agents.stateToolBindingFactory.ReadyToSignTransactionStrategy.WaitingForConfirmationStrategy",
        "RANSACTION_FAILED":"app.agents.stateToolBindingFactory.ReadyToSignTransactionStrategy.RANSACTIONFAILEDStrategy",
        "REQUEST_MORE_INFO":"app.agents.stateToolBindingFactory.ReadyToSignTransactionStrategy.REQUESTMOREINFOStrategy",
        "DISPLAY_QR_CODE":"app.agents.stateToolBindingFactory.ReadyToSignTransactionStrategy.DISPLAYQRCODEStrategy",
        "CONFIRM_SWAP":"app.agents.stateToolBindingFactory.ReadyToSignTransactionStrategy.CONFIRMSWAPStrategy",
    }

    @classmethod
    def get_strategy(cls, state: str) -> StateStrategy:
        class_path = cls.strategies.get(state)
        if class_path:
            # 确保 class_path 是一个字符串
            if isinstance(class_path, str):
                # 使用 rsplit 分割模块路径和类名
                module_name, class_name = class_path.rsplit('.', 1)
                # 动态导入模块
                module = import_module(module_name)
                # 获取类对象
                strategy_class = getattr(module, class_name)
                # 返回实例化的类
                return strategy_class()
            else:
                raise ValueError(f"策略路径 {class_path} 不是有效的字符串路径")

        raise ValueError(f"未找到状态 {state} 的策略")
