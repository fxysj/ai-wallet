import uvicorn
from fastapi import FastAPI
from travel_ai.app.api.routes import router

app = FastAPI()
app.include_router(router, prefix="/api")
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
# 启动方法：uvicorn main:app --reload
