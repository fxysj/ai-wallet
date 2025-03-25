# 定义 DictManager 类
from typing import Dict


class DictManager:
    def __init__(self):
        # 初始化存储数据的字典
        self.data: Dict[str, dict] = {}

    def add(self, key: str, value: dict) -> None:
        """
        向字典中添加一个键值对
        :param key: 键
        :param value: 值
        """
        if key in self.data:
            print(f"键 {key} 已存在，若要更新请使用 update 方法。")
        else:
            self.data[key] = value

    def delete(self, key: str) -> None:
        """
        从字典中删除指定键的项
        :param key: 要删除的键
        """
        if key in self.data:
            del self.data[key]
        else:
            print(f"键 {key} 不存在，无法删除。")

    def update(self, key: str, new_value: dict) -> None:
        """
        更新字典中指定键的值
        :param key: 要更新的键
        :param new_value: 新的值
        """
        if key in self.data:
            self.data[key] = new_value
        else:
            print(f"键 {key} 不存在，无法更新。若要添加请使用 add 方法。")

    def get(self, key: str) -> dict or None:
        """
        获取字典中指定键的值
        :param key: 要获取的键
        :return: 对应的值，如果键不存在则返回 None
        """
        return self.data.get(key)

    def get_all(self) -> Dict[str, dict]:
        """
        获取字典中的所有数据
        :return: 存储的所有数据
        """
        return self.data

    def extend(self, new_data: Dict[str, dict]) -> None:
        """
        将另一个 Dict[str, dict] 类型的数据合并到当前管理的数据字典中
        :param new_data: 要合并的新数据
        """
        for key, value in new_data.items():
            if key in self.data:
                print(f"键 {key} 已存在，将更新其值。")
                self.data[key] = value
            else:
                self.data[key] = value


dict_manager = DictManager()