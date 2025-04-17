import asyncio
import functools
from typing import Type, Optional
from pydantic import BaseModel
from .telemetry import LLMTelemetry
from .event import EventDispatcher, LLMEvent
from datetime import datetime


def llm_service_wrapper(func):
    @functools.wraps(func)
    async def wrapper(self, prompt_data: dict, response_model: Type[BaseModel], *args, **kwargs):
        telemetry = LLMTelemetry()
        event_dispatcher = EventDispatcher()

        # Record start time
        start_time = datetime.now()

        # Dispatch request event
        await event_dispatcher.dispatch_event(
            LLMEvent("llm_request", prompt_data)
        )

        try:
            # 这里调用原始函数时务必使用 await，如果原函数是异步的
            # 如果原函数不是异步的，就不要用 await
            if asyncio.iscoroutinefunction(func):
                result = await func(self, prompt_data, response_model, *args, **kwargs)
            else:
                result = func(self, prompt_data, response_model, *args, **kwargs)

            # Record metrics
            telemetry.record_metric({
                'model_name': 'gpt-4',
                'prompt_tokens': len(str(prompt_data)),
                'completion_tokens': len(str(result)),
                'total_tokens': len(str(prompt_data)) + len(str(result)),
                'latency': (datetime.now() - start_time).total_seconds(),
                'timestamp': datetime.now(),
                'status': 'success',
                'cost': 0.0  # Calculate actual cost based on your pricing
            })

            # Dispatch response event
            await event_dispatcher.dispatch_event(
                LLMEvent("llm_response", result)
            )

            return result

        except Exception as e:
            # Record error metrics
            telemetry.record_metric({
                'model_name': 'gpt-4',
                'prompt_tokens': len(str(prompt_data)),
                'completion_tokens': 0,
                'total_tokens': len(str(prompt_data)),
                'latency': (datetime.now() - start_time).total_seconds(),
                'timestamp': datetime.now(),
                'status': 'error',
                'cost': 0.0
            })

            # Dispatch error event
            await event_dispatcher.dispatch_event(
                LLMEvent("llm_error", str(e))
            )

            raise e

    return wrapper
