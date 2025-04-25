from app.agents.tools import get_nested_description


def update_session_history(session: dict, user_input_object, result, session_id: str, redis_dict_manager):
    """
    更新用户会话历史，仅保留最新的10条（即5轮对话）
    """
    if session.get("history") is None:
        session["history"] = []

    # 添加当前对话
    session["history"].extend([
        {"role": "user", "content": user_input_object.content, "data": user_input_object.data},
        {"role": "system", "content": get_nested_description(result), "data": result}
    ])

    # 仅保留最新的10条记录（5轮）
    session["history"] = session["history"][-10:]

    # 更新 Redis 缓存
    redis_dict_manager.update(session_id, session)