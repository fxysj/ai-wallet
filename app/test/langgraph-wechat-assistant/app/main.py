#FastAPI 主应用，接入公众号/企微消息
# main.py
from fastapi import FastAPI
from  .wechat_api import router as wechat_router

app = FastAPI()
app.include_router(wechat_router)
