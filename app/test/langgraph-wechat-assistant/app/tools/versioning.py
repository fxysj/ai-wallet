#用户版本存储 & 对比（模拟实现）
# tools/versioning.py
import os
import json
from difflib import SequenceMatcher

BASE_DIR = "data/versions"
os.makedirs(BASE_DIR, exist_ok=True)

import os
from dotenv import load_dotenv

load_dotenv()
enable_version_compare = os.getenv("ENABLE_VERSION_COMPARE", "0") == "1"
version_storage = {}

def get_version_file(user_id: str):
    return os.path.join(BASE_DIR, f"{user_id}.json")

def save_user_version(user_id: str, comments: list[str]) -> str:
    version_file = get_version_file(user_id)
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    return f"saved_version_for_{user_id}"

def compare_versions(user_id: str, new_comments: list[str]) -> dict:
    version_file = get_version_file(user_id)
    if not os.path.exists(version_file):
        return {"status": "no_previous_version", "similarity": 0.0}

    with open(version_file, "r", encoding="utf-8") as f:
        old_comments = json.load(f)

    old_text = "\n".join(old_comments)
    new_text = "\n".join(new_comments)
    similarity = SequenceMatcher(None, old_text, new_text).ratio()

    return {
        "status": "compared",
        "similarity": round(similarity, 4),
        "diff_summary": f"{int(similarity * 100)}% similar to last version"
    }
