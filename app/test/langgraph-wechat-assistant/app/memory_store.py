# Redis 用户状态和记忆
# memory_store.py
import redis
import os, json
from dotenv import load_dotenv

load_dotenv()
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True
)
def save_memory(user_id, data):
    r.set(f"user:{user_id}:memory", json.dumps(data), ex=3600)

def get_memory_by_user(user_id):
    value = r.get(f"user:{user_id}:memory")
    return json.loads(value) if value else None
