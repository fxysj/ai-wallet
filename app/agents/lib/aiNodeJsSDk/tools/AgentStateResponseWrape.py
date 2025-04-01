import json

from fastapi import HTTPException

from app.agents.schemas import AgentState


def stream_text_agent_state(content: str, data: any):
    # 创建一个数组来存放数据
    output_data = []

    # 1. 先处理 content 字符串
    if isinstance(content, str):
        for char in content:
            # 将每个字符编码为 Unicode 转义格式
            encoded_char = char.encode('unicode_escape').decode('utf-8')
            yield f'0:"{encoded_char}"\n'

    # 2. 将 data 添加到 output_data 数组中
    if isinstance(data, (dict, list)):
        output_data.append(data)
    else:
        output_data.append({"error": "Invalid data format"})

    # 3. 最后输出整个 data 数组
    formatted_data = json.dumps(output_data)
    yield f'2:{formatted_data}\n'


async def generate_chat_responses(chain,state:AgentState):
    full_response = ""
    try:
        async for chunk in chain.astream(state):
            # Accumulate the chunks
            full_response += chunk

            # Stream the chunk to the client
            yield f'2:[{{"result" : "{chunk}"}}]\n'
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Save the accumulated response to the database even if streaming was interrupted
        if full_response:
            # Save to DB logic
            ...

import json

def stream_text_agent_state_sin(content: str, data: any):
    # 创建一个数组来存放数据
    output_data = []

    # 1. 先处理 content 字符串
    if isinstance(content, str):
        for char in content:
            # 将每个字符编码为 Unicode 转义格式
            encoded_char = char.encode('unicode_escape').decode('utf-8')
            yield f'0:"{encoded_char}"\n'

    # 2. 处理 data 如果是字典，逐个字段进行 chunk 处理
    if isinstance(data, dict):
        for key, value in data.items():
            # 每一个字段进行分块处理
            yield f'1:"{key}":'
            if isinstance(value, str):
                for char in value:
                    # 将每个字符编码为 Unicode 转义格式
                    encoded_char = char.encode('unicode_escape').decode('utf-8')
                    yield f'0:"{encoded_char}"\n'
            else:
                # 对于非字符串类型，直接返回值
                yield f'0:{json.dumps(value)}\n'
    elif isinstance(data, (list, tuple)):
        # 处理 list 或 tuple 数据
        for item in data:
            yield f'1:{json.dumps(item)}\n'
    else:
        # 错误处理
        output_data.append({"error": "Invalid data format"})

    # 3. 最后输出整个 data 数组（如果有的话）
    if len(output_data) > 0:
        formatted_data = json.dumps(output_data)
        yield f'2:{formatted_data}\n'

def stream_text_agent_state_transfor(content: str, data: dict):
    # 如果 data 是字典格式，将其转换为列表包含字典
    annotations = data if isinstance(data, list) else [data]

    # 创建一个数组来存放数据
    output_data = []

    try:
        if not isinstance(content, str):
            raise TypeError("Content must be a string")

        # 使用正则表达式保持空格
        import re
        # 匹配单词和空格，保持原始顺序
        tokens = re.findall(r'\S+|\s+', content)

        for token in tokens:
            if token.strip():  # 如果是单词
                yield f'0:"{token}"\n'
            else:  # 如果是空格
                yield f'0:" "\n'
    except Exception as e:
        print(f"Error processing content: {e}")
        yield None

    # 2. 处理 annotations 部分，转换为 JSON 格式并输出 8: 格式
    if isinstance(annotations, list):
        formatted_annotations = json.dumps(annotations, ensure_ascii=False)
        yield f'8:{formatted_annotations}\n'  # 输出 annotations 部分

if __name__ == '__main__':
    # 示例数据：content 是一个字符串，data 是一个字典或数组
    #按照默认空格进行切分
    content = "address is not sysnc hellpwpored"
    data_dict = {"role": "system",
                 "content": content,
                 "proAction": ["1", "2"],
                 "data": {
                     "state": "1",
                     "form": {
                         "chainIndex": "11"
                     },
                     "indent": "send",
                 }
                 }
    # data_list = [{"key": "object1"}, {"anotherKey": "object2"}]

    # 使用生成器输出结果
    for chunk in stream_text_agent_state_transfor(content, data_dict):
        print(chunk)
