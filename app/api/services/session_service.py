import uuid

from app.agents.tools import get_nested_description
from app.api.chat_api import redis_dict_manager


def init_session(session_id):
    session = redis_dict_manager.get(session_id)
    if session is None:
        session = {"history": [], "data": {}, "session_id": str(uuid.uuid4())}
        redis_dict_manager.add(session_id, session)
    return session

def update_session_history(session, user_input_object, result, session_id):
    history = session.get("history", [])
    history.append({"role": "user", "content": user_input_object.content, "data": user_input_object.data})
    history.append({"role": "system", "content": get_nested_description(result), "data": result})
    session["history"] = history[-10:]  # 保留最近 10 条
    redis_dict_manager.update(session_id, session)
