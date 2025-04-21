from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.test.langGraph.main import run_sentiment_loop

app = FastAPI()

class SentimentRequest(BaseModel):
    comments: List[str]
    user_id: str

@app.post("/run-loop")
def run_loop(req: SentimentRequest):
    return run_sentiment_loop(req.comments, req.user_id)
