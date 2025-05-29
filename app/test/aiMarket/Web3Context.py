from pydantic import BaseModel
from typing import List

class Web3Context(BaseModel):
    id: str
    title: str
    logo: str
    type: int
    detail: str
    chain_id: int
    contract_addresses: List[str]
    symbol: str
