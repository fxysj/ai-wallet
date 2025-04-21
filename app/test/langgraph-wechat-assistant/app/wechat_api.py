# 微信公众号服务端逻辑
# wechat_api.py
from fastapi import APIRouter, Request
from hashlib import sha1
import time, xml.etree.ElementTree as ET
from langgraph_flow import run_sentiment_loop
import os
from dotenv import load_dotenv
load_dotenv()
router = APIRouter()
TOKEN = os.getenv("WECHAT_TOKEN", "default_token")

@router.get("/wechat")
def verify(signature: str, timestamp: str, nonce: str, echostr: str):
    tmp = "".join(sorted([TOKEN, timestamp, nonce]))
    return echostr if sha1(tmp.encode()).hexdigest() == signature else "error"

@router.post("/wechat")
async def handle_msg(request: Request):
    xml = ET.fromstring(await request.body())
    msg_type = xml.find("MsgType").text
    user_input = xml.find("Content").text
    user_id = xml.find("FromUserName").text
    to_user = xml.find("ToUserName").text

    if msg_type == "text":
        result = run_sentiment_loop([user_input], user_id)
        content = result["final_result"]

        reply = f"""
        <xml>
          <ToUserName><![CDATA[{user_id}]]></ToUserName>
          <FromUserName><![CDATA[{to_user}]]></FromUserName>
          <CreateTime>{int(time.time())}</CreateTime>
          <MsgType><![CDATA[text]]></MsgType>
          <Content><![CDATA[{content}]]></Content>
        </xml>
        """
        return reply
