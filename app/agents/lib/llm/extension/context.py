from typing import Dict, List, Any, Optional


class LLMContext:
    def __init__(self):
        self.conversation_history: List[dict] = []
        self.metadata: Dict[str, Any] = {}
        self.system_prompts: List[str] = []
        self.context_variables: Dict[str, Any] = {}

    def add_to_history(self, message: dict):
        self.conversation_history.append(message)

    def get_context_window(self, window_size: int) -> List[dict]:
        return self.conversation_history[-window_size:]

    def set_metadata(self, key: str, value: Any):
        self.metadata[key] = value