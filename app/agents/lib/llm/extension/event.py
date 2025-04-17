import asyncio
from typing import Callable, Dict, List, Any
from datetime import datetime


class LLMEvent:
    def __init__(self, event_type: str, data: Any):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()


class EventDispatcher:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventDispatcher, cls).__new__(cls)
            cls._instance.handlers = {}
            cls._instance.event_queue = asyncio.Queue()
        return cls._instance

    def register_handler(self, event_type: str) -> Callable:
        def decorator(handler: Callable):
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)
            return handler

        return decorator

    async def dispatch_event(self, event: LLMEvent):
        if event.event_type in self.handlers:
            for handler in self.handlers[event.event_type]:
                await handler(event)
        await self.event_queue.put(event)