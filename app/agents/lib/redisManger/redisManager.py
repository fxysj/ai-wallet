import redis
import json
from typing import Dict, Optional
from app.config import settings

class RedisDictManager:
    def __init__(self, redis_host=settings.REDIS_HOST, redis_port=settings.REDIS_PORT, redis_db=settings.REDIS_DB):
        """
        初始化 Redis 连接
        :param redis_host: Redis 服务器地址
        :param redis_port: Redis 端口
        :param redis_db: Redis 数据库索引
        """
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        self.namespace = "dict_manager:"  # 添加命名空间，防止键冲突

    def add(self, key: str, value: dict) -> None:
        """
        向 Redis 中添加一个键值对
        :param key: 键
        :param value: 值 (dict)
        """
        redis_key = self.namespace + key
        print("redis_key"+redis_key)
        if self.redis_client.exists(redis_key):
            print(f"键 {key} 已存在，若要更新请使用 update 方法。")
            self.update(key,value)
        else:
            self.redis_client.set(redis_key, json.dumps(value))

    def delete(self, key: str) -> None:
        """
        从 Redis 中删除指定键
        :param key: 要删除的键
        """
        redis_key = self.namespace + key
        if self.redis_client.exists(redis_key):
            self.redis_client.delete(redis_key)
        else:
            print(f"键 {key} 不存在，无法删除。")

    def update(self, key: str, new_value: dict) -> None:
        """
        更新 Redis 中指定键的值
        :param key: 要更新的键
        :param new_value: 新的值 (dict)
        """
        redis_key = self.namespace + key
        if self.redis_client.exists(redis_key):
            self.redis_client.set(redis_key, json.dumps(new_value))
        else:
            print(f"键 {key} 不存在，无法更新。若要添加请使用 add 方法。")

    def get(self, key: str) -> Optional[dict]:
        """
        获取 Redis 中指定键的值
        :param key: 要获取的键
        :return: 对应的值 (dict)，如果键不存在则返回 None
        """
        redis_key = self.namespace + key
        value = self.redis_client.get(redis_key)
        return json.loads(value) if value else None

    def get_all(self) -> Dict[str, dict]:
        """
        获取 Redis 中所有存储的数据
        :return: 存储的所有数据 (Dict[str, dict])
        """
        all_keys = self.redis_client.keys(self.namespace + "*")
        all_data = {}
        for redis_key in all_keys:
            key = redis_key.replace(self.namespace, "")  # 移除命名空间前缀
            value = self.redis_client.get(redis_key)
            all_data[key] = json.loads(value) if value else None
        return all_data

    def extend(self, new_data: Dict[str, dict]) -> None:
        """
        将另一个 Dict[str, dict] 类型的数据合并到当前 Redis 存储中
        :param new_data: 要合并的新数据
        """
        for key, value in new_data.items():
            redis_key = self.namespace + key
            if self.redis_client.exists(redis_key):
                print(f"键 {key} 已存在，将更新其值。")
            self.redis_client.set(redis_key, json.dumps(value))
redis_dict_manager = RedisDictManager()
if __name__ == '__main__':
    # 实例化 RedisDictManager
    redis_dict_manager = RedisDictManager()

    # 示例操作
    redis_dict_manager.add("user:1", {"name": "Alice", "balance": 100})
    redis_dict_manager.add("user:2", {"name": "Bob", "balance": 200})

    print(redis_dict_manager.get("user:1"))  # {"name": "Alice", "balance": 100}
    print(redis_dict_manager.get_all())  # 获取所有键值对
    redis_dict_manager.update("user:1", {"name": "Alice", "balance": 150})
    redis_dict_manager.delete("user:2")

