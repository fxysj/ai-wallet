from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, Any

class ThoughtCaptureHandler(BaseCallbackHandler):
    def __init__(self, initial_state: Dict[str, Any]):
        self.state = initial_state

    def on_llm_new_token(self, token: str, **kwargs):
        if "thoughts" not in self.state:
            self.state["thoughts"] = ""
        self.state["thoughts"] += token  # 实时拼接 token

    def on_llm_end(self, response, **kwargs):
        # 最终也可以在结束时处理完整内容
        print("LLM completed, full output captured.")
