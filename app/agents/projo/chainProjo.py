from typing import Optional, List, Dict
from pydantic import BaseModel

class Token(BaseModel):
    symbol: str
    name: str
    address: Optional[str]
    balance: str
    decimals: int

class Chain(BaseModel):
    id: int
    name: str
    symbol: str
    color: str

class ChainData(BaseModel):
    NETWORK_CHAIN_ID: Dict[str, int]
    CHAINS: List[Chain]
    TOKENS: Dict[str, List[Token]]
