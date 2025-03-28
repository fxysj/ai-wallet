import json


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



if __name__ == '__main__':
    # 示例数据：content 是一个字符串，data 是一个字典或数组
    content = "你好！"
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
    for chunk in stream_text_agent_state(content, data_dict):
        print(chunk)
