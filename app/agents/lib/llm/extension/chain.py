from typing import List, Callable, Optional, Type
from pydantic import BaseModel


class ChainNode:
    def __init__(self, model: str, prompt_template: str,name: Optional[str] = None):
        self.model = model
        self.prompt_template = prompt_template
        self.next_nodes: List['ChainNode'] = []
        self.condition: Optional[Callable] = None
        self.name = name or f"Node-{id(self)}"

    def add_next(self, node: 'ChainNode', condition: Optional[Callable] = None):
        self.next_nodes.append(node)
        self.condition = condition
        return self