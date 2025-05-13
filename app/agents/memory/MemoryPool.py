from app.agents.memory.SummaryRedisMemory import SummaryRedisMemory


class MemoryPool:
    _pool: dict[str, SummaryRedisMemory] = {}

    @classmethod
    def get(cls, user_id: str,url) -> SummaryRedisMemory:
        if user_id not in cls._pool:
            cls._pool[user_id] = SummaryRedisMemory(
                redis_url=url,
                session_id=user_id,
                max_token_limit=1000
            )
        return cls._pool[user_id]
