import json
from typing import Dict, Optional

from app.agents.schemas import AgentState

# Constants for chain data
NETWORK_CHAIN_ID = {
    "BTC": 0,
    "ETHEREUM": 60,
    "BSC": 56,
    "SOLANA": 501,
    "TRON": 195
}

# Default chain data used if no chain data is provided in state
DEFAULT_CHAIN_DATA = {
    "NETWORK_CHAIN_ID": NETWORK_CHAIN_ID,
    "CHAINS": [
        {
            "id": NETWORK_CHAIN_ID["ETHEREUM"],
            "name": "ETHEREUM",
            "symbol": "ETH",
            "color": "#627EEA"
        },
        {
            "id": NETWORK_CHAIN_ID["BSC"],
            "name": "BSC",
            "symbol": "BSC",
            "color": "#F3BA2F"
        },
        {
            "id": NETWORK_CHAIN_ID["TRON"],
            "name": "TRON",
            "symbol": "TRON",
            "color": "#FF0013"
        },
        {
            "id": NETWORK_CHAIN_ID["SOLANA"],
            "name": "SOLANA",
            "symbol": "SOLANA",
            "color": "#14F195"
        }
    ],
    "TOKENS": {
        str(NETWORK_CHAIN_ID["ETHEREUM"]): [
            {
                "symbol": "ETH",
                "name": "ETH",
                "address": None,
                "balance": "1.256",
                "decimals": 18
            },
            {
                "symbol": "USDT",
                "name": "Tether",
                "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
                "balance": "350.00",
                "decimals": 18
            },
            {
                "symbol": "USDC",
                "name": "USD Coin",
                "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                "balance": "175.50",
                "decimals": 18
            }
        ],
        str(NETWORK_CHAIN_ID["BSC"]): [
            {
                "symbol": "BNB",
                "name": "BNB",
                "address": None,
                "balance": "0.1761",
                "decimals": 18
            },
            {
                "symbol": "USDT",
                "name": "Tether",
                "address": "0x55d398326f99059ff775485246999027b3197955",
                "balance": "10.22",
                "decimals": 18
            },
            {
                "symbol": "USDC",
                "name": "USD Coin",
                "address": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
                "balance": "0",
                "decimals": 18
            }
        ],
        str(NETWORK_CHAIN_ID["TRON"]): [
            {
                "symbol": "TRX",
                "name": "TRX",
                "address": None,
                "balance": "76.22",
                "decimals": 6
            },
            {
                "symbol": "USDT",
                "name": "Tether",
                "address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                "balance": "123.414",
                "decimals": 6
            },
            {
                "symbol": "USDC",
                "name": "USD Coin",
                "address": "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8",
                "balance": "98.146",
                "decimals": 6
            }
        ],
        str(NETWORK_CHAIN_ID["SOLANA"]): [
            {
                "symbol": "SOL",
                "name": "SOLANA",
                "address": None,
                "balance": "8.75",
                "decimals": 9
            },
            {
                "symbol": "USDT",
                "name": "Tether",
                "address": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
                "balance": "784.12",
                "decimals": 6
            },
            {
                "symbol": "USDC",
                "name": "USD Coin",
                "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "balance": "0.00",
                "decimals": 6
            }
        ]
    }
}