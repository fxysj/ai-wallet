from pydantic import BaseModel
from typing import List

class ActionItem(BaseModel):
    title: str         # 行动标题，例如“查看最新市场行情”
    description: str   # 行动描述，简要说明该行动的内容和意义

class ToolItem(BaseModel):
    name: str          # 工具名称，如“CoinMarketCap”
    description: str   # 工具功能简述，比如“主流币种行情与资讯平台”
    url: str           # 工具访问链接，方便用户直接跳转使用

class NewsItem(BaseModel):
    title: str         # 新闻标题
    content: str       # 新闻简要内容或摘要
    url: str           # 新闻链接，方便用户阅读详情
    date: str          # 发布时间，格式为“YYYYMMDD”，例如“20250604”

class Overstation(BaseModel):
    investment_advice: str              # 投资建议文本，针对用户当前情况给出的专业指导
    hot_news: List[NewsItem]           # 当前热点新闻列表，每条新闻包含标题、内容、链接和发布时间，按时间最新排序
    next_actions: List[ActionItem]     # 推测用户下一步可能采取的行动列表，每个是ActionItem结构
    tools: List[ToolItem]              # 推荐给用户的工具列表，帮助其辅助决策和操作，每个是ToolItem结构
