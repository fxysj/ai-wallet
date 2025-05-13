#新闻智能体测试
import json

from app.agents.tasks.news_task import getNewSearch
def getNews():
    res = getNewSearch("latest")
    print(json.dumps(res,indent=2, ensure_ascii=False))
if __name__ == '__main__':
    getNews()