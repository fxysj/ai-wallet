import os
import json
from difflib import SequenceMatcher

# 定义提示词版本存储目录
BASE_DIR = "data/prompt_versions"
os.makedirs(BASE_DIR, exist_ok=True)

# 获取提示词版本文件路径
def get_prompt_version_file(prompt_name: str, version: str):
    return os.path.join(BASE_DIR, f"{prompt_name}_{version}.json")

# 保存提示词版本
def save_prompt_version(prompt_name: str, version: str, prompt_content: str) -> str:
    version_file = get_prompt_version_file(prompt_name, version)
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump({"prompt": prompt_content}, f, ensure_ascii=False, indent=2)
    return f"saved_version_{version}_for_{prompt_name}"

# 获取提示词版本内容
def get_prompt_version(prompt_name: str, version: str) -> str:
    version_file = get_prompt_version_file(prompt_name, version)
    if not os.path.exists(version_file):
        return None
    with open(version_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["prompt"]

# 更新提示词版本
def update_prompt_version(prompt_name: str, new_version: str, new_prompt_content: str) -> str:
    return save_prompt_version(prompt_name, new_version, new_prompt_content)

# 对比提示词版本
def compare_prompt_versions(prompt_name: str, old_version: str, new_version: str) -> dict:
    old_prompt = get_prompt_version(prompt_name, old_version)
    new_prompt = get_prompt_version(prompt_name, new_version)
    if not old_prompt or not new_prompt:
        return {"status": "version_not_found", "similarity": 0.0}
    similarity = SequenceMatcher(None, old_prompt, new_prompt).ratio()
    return {
        "status": "compared",
        "similarity": round(similarity, 4),
        "diff_summary": f"{int(similarity * 100)}% similar to last version"
    }

# 回滚提示词版本
def rollback_prompt_version(prompt_name: str, target_version: str, current_version: str) -> str:
    target_prompt = get_prompt_version(prompt_name, target_version)
    if not target_prompt:
        return f"Target version {target_version} not found."
    return update_prompt_version(prompt_name, current_version, target_prompt)

# 示例使用
if __name__ == "__main__":
    prompt_name = "transfer_prompt"
    # 保存初始版本
    version_1 = "v1.0"
    prompt_content_1 = """
    你是一个专业的区块链转账助手，请根据用户输入完成转账信息的收集和处理。
    用户输入: {query}
    ...
    """
    save_prompt_version(prompt_name, version_1, prompt_content_1)

    # 保存新版本
    version_2 = "v2.0"
    prompt_content_2 = """
    你是一个专业的区块链转账助手，精通各类加密资产的转账操作。
    用户输入: {query}
    ...
    """
    update_prompt_version(prompt_name, version_2, prompt_content_2)

    # 对比版本
    comparison = compare_prompt_versions(prompt_name, version_1, version_2)
    print("版本对比结果:", comparison)

    # 回滚版本
    rollback_result = rollback_prompt_version(prompt_name, version_1, version_2)
    print("回滚结果:", rollback_result)