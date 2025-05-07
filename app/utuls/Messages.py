import json
from typing import List, Dict, Any, Optional


class Message:
    """ 代表一个消息对象 """

    def __init__(self, role: str, content: str, data: Any):
        self.role = role
        self.content = content
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        """ 转换为字典 """
        return {
            "role": self.role,
            "content": self.content,
            "data": self.data
        }

    def __repr__(self) -> str:
        """ 定义对象的可读字符串表示 """
        return f"Message(role='{self.role}', content='{self.content}', data={self.data})"


class Session:
    """ 代表一个用户会话，提供静态方法来处理消息 """

    @staticmethod
    def get_last_user_message(session_data: Dict[str, Any]) -> Optional[Message]:
        """
        获取 messages 列表中最后一个 role 为 'user' 的消息对象（返回 Message 对象）

        :param session_data: 包含 session_id 和 messages 列表的 JSON 数据
        :return: 最后一个用户消息对象（如果存在），否则返回 None
        """
        messages: List[Dict[str, Any]] = session_data.get("messages", [])

        for message in reversed(messages):  # 逆序遍历
            if message.get("role") == "user":
                return Message(
                    role=message["role"],
                    content=message["content"],
                    data=message.get("data", {})
                )
        return None  # 如果没有找到则返回 None

    @staticmethod
    def get_recent_history(session_data: Dict[str, Any], count: int = 5) -> str:
        """
        获取最近 N 条对话历史，格式化为字符串

        :param session_data: 包含 session_id 和 messages 列表的 JSON 数据
        :param count: 要获取的历史消息条数，默认为 5
        :return: 格式化的对话历史字符串
        """
        messages: List[Dict[str, Any]] = session_data.get("messages", [])
        recent_messages = messages[-count:]  # 取最近 count 条消息

        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])

    @classmethod
    def getSessionHistory(cls, session, limit=5):
        """
        返回格式化的最近若干条对话历史，每条记录一行，格式为 'role: content'。

        Args:
            session (dict): session 对象
            limit (int): 限制返回的记录条数

        Returns:
            str: 格式化的历史记录字符串
        """
        history = session.get("history", [])
        recent_messages = history[-limit:] if limit else history
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])


if __name__ == '__main__':
    # 模拟一个 session 字典
    session = {
        "history": [
            {"role": "user", "content": "你好", "data": {}},
            {"role": "system", "content": "你好，有什么可以帮您？", "data": {}},
            {"role": "user", "content": "我想查天气", "data": {}},
            {"role": "system", "content": "请问你在哪个城市？", "data": {}},
            {"role": "user", "content": "北京", "data": {}},
            {"role": "system", "content": "北京今天晴，气温 25℃", "data": {}},
        ]
    }

    # 调用方法，获取最近 3 条对话
    output = Session.getSessionHistory(session, limit=20)
    print(output)
    # 示例 JSON 数据
    # session_json = '''
    # {
    #   "session_id": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12",
    #   "messages": [
    #     {
    #       "role": "user",
    #       "content": "转账",
    #       "data": {}
    #     },
    #     {
    #       "role": "system",
    #       "content": "你需要办理的是什么转账的业务?",
    #       "data": {}
    #     },
    #     {
    #       "role": "user",
    #       "content": "我要向0x1113 进行转入 3个ETH",
    #       "data": {}
    #     },
    #     {
    #       "role": "system",
    #       "content": "ok 我明白您的意思啦 您的意思是希望向0x113这个地址进行转入3个ETH类型的对吧?",
    #       "Success": true,
    #       "message": "ok",
    #       "promentNexttAction": [],
    #       "intent": "send",
    #       "data": {
    #         "state": "完成",
    #         "form": {
    #           "chainIndex": "ETH",
    #           "fromAddr": "",
    #           "toAddr": "0x113",
    #           "txAmount": "3",
    #           "tokenSymbol": "",
    #           "tokenAddress": "",
    #           "extJson": ""
    #         },
    #         "missFields": [
    #           {
    #             "name": "chainIndex",
    #             "description": "区块链索引"
    #           }
    #         ],
    #         "DxTransActionDetail": {}
    #       }
    #     }
    #   ]
    # }
    # '''
    #
    # # 解析 JSON 数据
    # session_data = json.loads(session_json)
    #
    # # 直接调用静态方法获取最后一条用户消息
    # last_user_message = Session.get_last_user_message(session_data)
    #
    # # 打印对象
    # print(last_user_message)
    #
    # # 如果需要转换为字典格式
    # print(json.dumps(last_user_message.to_dict(), indent=2, ensure_ascii=False) if last_user_message else "未找到用户消息")
    #
    # # 获取最近 5 条对话历史（默认）
    # recent_history = Session.get_recent_history(session_data)
    # print("最近 5 条对话记录:\n", recent_history)
    #
    # # 获取最近 3 条对话历史
    # recent_history_3 = Session.get_recent_history(session_data, count=3)
    # print("\n最近 3 条对话记录:\n", recent_history_3)


