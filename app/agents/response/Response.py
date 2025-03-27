import json


class SystemResponse:
    """
    系统服务构建返回
    """

    def __init__(
        self,
        is_success: bool,
        content: str,
        message: str,
        prompt_next_action: list,
        data: any,
        intent: str = "",
    ):
        """
        构造一个系统响应对象

        :param is_success: bool - 响应是否成功
        :param content: str - 外部注入的字符串，用于 system 消息内容
        :param message: str - 外部注入的消息字段（成功或错误消息）
        :param prompt_next_action: list - 外部注入的数组，用于提示下一步动作
        :param data: any - 外部注入的任意类型数据
        :param intent: str - （可选）意图字段，默认为空字符串
        """
        self.role = "system"
        self.content = content
        self.success = is_success
        self.message = message
        self.promptNextAction = prompt_next_action
        self.data = data
        if intent:
            self.intent = intent

    @staticmethod
    def success(
        prompt_next_action: list,
        data: any,
        content: str,
        intent: str = "",
        message: str = "ok",
    ):
        """
        创建一个成功响应的对象

        :param prompt_next_action: list - 外部注入的数组，用于提示下一步动作
        :param data: any - 外部注入的任意类型数据
        :param content: str - 外部注入的字符串，用于 system 消息内容
        :param intent: str - （可选）意图字段，默认为空字符串
        :param message: str - （可选）消息字段，默认为 "ok"
        :return: SystemResponse - 成功响应对象
        """
        return SystemResponse(True, content, message, prompt_next_action, data, intent)

    @staticmethod
    def error(
        prompt_next_action: list,
        data: any,
        content: str,
        message: str,
        intent: str = "",
    ):
        """
        创建一个错误响应的对象

        :param prompt_next_action: list - 外部注入的数组，用于提示下一步动作
        :param data: any - 外部注入的任意类型数据
        :param content: str - 外部注入的字符串，用于 system 消息内容
        :param message: str - 外部注入的错误消息
        :param intent: str - （可选）意图字段，默认为空字符串
        :return: SystemResponse - 错误响应对象
        """
        return SystemResponse(False, content, message, prompt_next_action, data, intent)

    def to_dict(self):
        """
        将对象转换为字典格式，并过滤掉 None 值字段
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @staticmethod
    def error_with_message(message: str):
        """
        创建一个仅包含错误消息的错误响应对象

        :param message: str - 错误消息
        :return: SystemResponse - 仅包含错误消息的错误响应对象
        """
        return SystemResponse(
            is_success=False,
            content="ok",  # 默认错误提示
            message=message,
            prompt_next_action=[],  # 提示下一步动作
            data=None,
            intent="",
        )
    @staticmethod
    def errorWrap(prompt_next_action:[],message:str,data:dict):
        #需要这里根据 data 中返回的state indent进行结合判断
        return SystemResponse(
            is_success=False,
            content="ok",
            message=message,
            prompt_next_action=prompt_next_action,
            data=data
        )

    def to_dict(self):
        return {
            "success": self.success,
            "prompt_next_action": self.promptNextAction,
            "data": self.data,
            "content": self.content
        }


# if __name__ == '__main__':
#     # 示例调用
#     # 成功响应示例
#     success_response = SystemResponse.success(
#         ["下一步操作1", "下一步操作2"],  # promptNextAction 数组
#         {
#             "state": "完成",
#             "form": {
#                 "chainIndex": "ETH",
#                 "fromAddr": "",
#                 "toAddr": "0x113",
#                 "txAmount": "3",
#                 "tokenSymbol": "",
#                 "tokenAddress": "",
#                 "extJson": "",
#             },
#             "missFields": [{"name": "chainIndex", "description": "区块链索引"}],
#             "DxTransActionDetail": {},
#         },
#         "ok 我明白您的意思啦 您的意思是希望向0x113这个地址进行转入3个ETH类型的对吧?",  # content
#         "send",  # intent
#     )
#
#     # 错误响应示例
#     error_response = SystemResponse.error(
#         ["请检查表单信息"],
#         None,
#         "表单验证失败，请补全必填项",  # content
#         "OK",  # 错误消息
#     )
#
#     # 打印 JSON 结果
#     print("Success Response:", json.dumps(success_response.to_dict(), indent=2, ensure_ascii=False))
#     print("Error Response:", json.dumps(error_response.to_dict(), indent=2, ensure_ascii=False))



