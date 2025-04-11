import json
from typing import Optional, List


class SystemResponse:
    """
    系统服务构建返回
    """

    def __init__(
        self,
        role:str,
        content:str,
        success: bool,
        message: str,
        data: any,
        promptedAction: Optional[List[str]] = None,
        confidence: float = 0.0,
            alternatives: Optional[List[str]] = None
    ):
        """
        构造一个系统响应对象

        :param success: bool - 响应是否成功
        :param message: str - 外部注入的字符串，用于 system 消息内容
        :param promptedAction: list - 外部注入的数组，用于提示下一步动作
        :param data: any - 外部注入的任意类型数据
        :param confidence:float - 大模型分数
        :param alternatives:list -额外的信息 工具调用信息列表
        """
        self.role = "system"
        self.content = content
        self.success = success
        self.message = message
        self.promptNextAction = promptedAction
        self.data = data
        self.confidence= confidence
        self.alternatives = alternatives
    @staticmethod
    def success(
        prompt_next_action: list,
        data: any,
        content: str,
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
        return SystemResponse(role="system",success=True, content=content, message=message, promptedAction=prompt_next_action, data=data,confidence=99.9,alternatives=[])

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
        return SystemResponse(role="system",success=False, content=content, message=message, promptedAction=prompt_next_action, data=data, confidence=99.9,alternatives=[])

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
            role="system",
            success=False,
            content="ok",  # 默认错误提示
            message=message,
            promptedAction=[],  # 提示下一步动作
            data={},
            confidence=99.9,
            alternatives=[],
        )
    @staticmethod
    def errorWrap(prompt_next_action:[],message:str,data:dict):
        #需要这里根据 data 中返回的state indent进行结合判断
        return SystemResponse(
            success=False,
            content="ok",
            message=message,
            promptedAction=prompt_next_action,
            data=data,
            confidence=99.9,
            alternatives=[],
        )

    def to_dict(self):
        return {
            "success": self.success,
            "promptedAction": self.promptNextAction,
            "data": self.data,
            #"content": self.content,
            "message":self.message,
            "confidence":self.confidence,
            "alternatives":self.alternatives,
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



