import json
from enum import Enum
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import BaseModel
from .attachment import ClientAttachment
import base64
from typing import List, Optional, Any, Dict


# 假设 ClientAttachment 类已经定义
# from .attachment import ClientAttachment

class ToolInvocationState(str, Enum):
    CALL = 'call'
    PARTIAL_CALL = 'partial-call'
    RESULT = 'result'


class ToolInvocation(BaseModel):
    state: ToolInvocationState
    toolCallId: str
    toolName: str
    args: Any
    result: Any


class ClientMessage(BaseModel):
    role: str
    content: str
    data: Dict
    experimental_attachments: Optional[List[ClientAttachment]] = None
    toolInvocations: Optional[List[ToolInvocation]] = None


def convert_to_openai_messages(messages: List[ClientMessage]) -> List[ChatCompletionMessageParam]:
    openai_messages = []

    for message in messages:
        parts = []
        tool_calls = []

        parts.append({
            'type': 'text',
            'text': message.content
        })

        if message.experimental_attachments:
            for attachment in message.experimental_attachments:
                try:
                    if attachment.contentType.startswith('image'):
                        parts.append({
                            'type': 'image_url',
                            'image_url': {
                                'url': attachment.url
                            }
                        })
                    elif attachment.contentType.startswith('text'):
                        parts.append({
                            'type': 'text',
                            'text': attachment.url
                        })
                except AttributeError:
                    # 处理 attachment 没有 contentType 或 url 属性的情况
                    continue

        if message.toolInvocations:
            for toolInvocation in message.toolInvocations:
                try:
                    tool_calls.append({
                        "id": toolInvocation.toolCallId,
                        "type": "function",
                        "function": {
                            "name": toolInvocation.toolName,
                            "arguments": json.dumps(toolInvocation.args)
                        }
                    })
                except (AttributeError, TypeError, ValueError):
                    # 处理 toolInvocation 属性缺失或 json 序列化异常的情况
                    continue

        tool_calls_dict = {"tool_calls": tool_calls} if tool_calls else {}

        openai_message = {
            "role": message.role,
            "content": parts,
            **tool_calls_dict
        }
        openai_messages.append(openai_message)

        if message.toolInvocations:
            for toolInvocation in message.toolInvocations:
                try:
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": toolInvocation.toolCallId,
                        "content": json.dumps(toolInvocation.result)
                    }
                    openai_messages.append(tool_message)
                except (AttributeError, TypeError, ValueError):
                    # 处理 toolInvocation 属性缺失或 json 序列化异常的情况
                    continue

    return openai_messages
