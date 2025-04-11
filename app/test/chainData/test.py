import unittest
from app.agents.projo.chainProjo import ChainData
class TestChainDataModel(unittest.TestCase):
    def test_chain_data(self):
        # 示例数据
        data = {
            "NETWORK_CHAIN_ID": {
                "BTC": 0,
                "ETHEREUM": 60,
                "BSC": 56,
                "SOLANA": 501,
                "TRON": 195
            },
            "CHAINS": [
                {
                    "id": 60,
                    "name": "ETHEREUM",
                    "symbol": "ETH",
                    "color": "#627EEA"
                },
                {
                    "id": 56,
                    "name": "BSC",
                    "symbol": "BSC",
                    "color": "#F3BA2F"
                }
            ],
            "TOKENS": {
                "60": [
                    {
                        "symbol": "ETH",
                        "name": "ETH",
                        "address": None,
                        "balance": "1.256",
                        "decimals": 18
                    }
                ],
                "56": [
                    {
                        "symbol": "BNB",
                        "name": "BNB",
                        "address": None,
                        "balance": "0.1761",
                        "decimals": 18
                    }
                ]
            }
        }

        # 创建 ChainData 实例
        chain_data = ChainData(**data)

        # 断言测试
        self.assertEqual(chain_data.NETWORK_CHAIN_ID["BTC"], 0)
        self.assertEqual(chain_data.CHAINS[0].name, "ETHEREUM")
        self.assertEqual(chain_data.TOKENS["60"][0].symbol, "ETH")

if __name__ == '__main__':
    unittest.main()
