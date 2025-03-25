from app.agents.schemas import Intention


class FieldChecker:
    """
    工具类 FieldChecker

    提供静态方法 get_field_info，用于检查给定数据（字典类型）中是否存在指定字段，
    如果存在则返回对应字段的信息，否则返回 False。
    """

    @staticmethod
    def get_field_info(data: dict, field_name: str):
        """
        获取数据中指定字段的信息

        :param data: dict 要检查的字典对象
        :param field_name: str 要查找的字段名称
        :return: 任意类型 - 如果字段存在，则返回字段对应的值；如果字段不存在，则返回 False
        """
        if not isinstance(data, dict):
            return False
        return data.get(field_name, False)

# if __name__ == '__main__':
#     # 示例调用
#     example_data = {
#         "chainIndex": "ETH",
#         "fromAddr": "",
#         "toAddr": "0x113",
#         "txAmount": "3"
#     }
#     fieldName = Intention.send
#     print(fieldName)
#     print(FieldChecker.get_field_info(example_data, field_name=fieldName))  # 输出 "ETH"
#     print(FieldChecker.get_field_info(example_data, "tokenSymbol"))  # 输出 False


