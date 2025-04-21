# 企业微信机器人推送逻辑
# wecom_bot.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("WECOM_WEBHOOK_URL")

def send_wecom_markdown(title: str, content: str):
    """
    企业微信机器人推送 Markdown 消息
    """
    if not WEBHOOK_URL:
        raise ValueError("企业微信 Webhook 未配置")

    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"#### {title}\n{content}"
        }
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 200:
        raise Exception(f"发送企业微信消息失败：{response.status_code}, {response.text}")
    return response.json()

def send_wecom_text(content: str):
    """
    企业微信机器人推送纯文本消息
    """
    if not WEBHOOK_URL:
        raise ValueError("企业微信 Webhook 未配置")

    data = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 200:
        raise Exception(f"发送企业微信文本失败：{response.status_code}, {response.text}")
    return response.json()
