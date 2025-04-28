#这里是RAG的路由方式
from fastapi import APIRouter
from app.agents.schemas import BaseResponse
from fastapi.requests import Request

from app.api.services.rag_service import RagService

#初始化路由
router = APIRouter()
rag_service = RagService()

@router.post("/add",description="""
RAG进行增加到向量数据库中
- 可以从网站进行获取 chains的信息: 地址:https://defillama.com/chains
- Brideged TVL:  https://defillama.com/bridged
- Comparse Chains: https://defillama.com/compare-chains?chains=OP+Mainnet&chains=Arbitrum
- Airdrops: https://defillama.com/airdrops
- Treasuries: https://defillama.com/treasuries
- Oracles: https://defillama.com/oracles

""")
async def ragAdd(url:str, request: Request):
    result = await rag_service.load_url_and_ingest(url)
    return BaseResponse().success(result)

@router.post("/query",description="查询接口")
async def query_rag(query_text: str, top_k: int = 5):
    result = await rag_service.similarity_search(query_text,top_k=top_k)
    return BaseResponse.success(result)

