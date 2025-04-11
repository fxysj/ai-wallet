import unittest
import datetime
import jwt

from app.agents.toolsUtils.tools import decode_and_validate_jwt


class TestJWTFunctions(unittest.TestCase):
    def setUp(self):
        self.secret_key = 'fibonacci_blx2024_be_with_you'
        self.algorithms = ['HS256']
        self.payload = {
            "EvmAddress": "0x980dd1c27614121231f5a64db9dd7c679c3551d2",
            "SolanaAddress": "8QAKrg9jHVeMrQj1ZKDPvzzqNM5dhmdXThfuApciko6a",
            "TronAddress": "TFrVnq1CcrjBgaFBvP2iLykJQQ6aoZ9Hf4",
            "user_id": "10010",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=60)  # 设置过期时间为60秒后
        }
        self.token = jwt.encode(self.payload, self.secret_key, algorithm=self.algorithms[0])

    def test_decode_and_validate_jwt(self):
        # 测试有效的 JWT
        #token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJFdm1BZGRyZXNzIjoiMHg5ODBkZDFjMjc2MTQxMjEyMzFmNWE2NGRiOWRkN2M2NzljMzU1MWQyIiwiU29sYW5hQWRkcmVzcyI6IjhRQUtyZzlqSFZlTXJRajFaS0RQdnp6cU5NNWRobWRYVGhmdUFwY3lrbzZhIiwiVHJvbkFkZHJlc3MiOiJURnJWbnExQ2NyakJnYUZCdlAyaUx5a0pRUTZhb1o5SGY0IiwidXNlcl9pZCI6InRlc3RfYWNjb3VudCJ9.LGYIEsiTsNXLkepao365smkvMGECUERuyVLZx6xNly0"
        decoded_payload = decode_and_validate_jwt(self.token, self.secret_key, self.algorithms)
        self.assertIsNotNone(decoded_payload)
        #print(decoded_payload)
        self.assertEqual(decoded_payload["user_id"], "10010")

    def test_expired_jwt(self):
        # 测试过期的 JWT
        expired_payload = self.payload.copy()
        expired_payload['exp'] = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)  # 设置为1秒前过期
        expired_token = jwt.encode(expired_payload, self.secret_key, algorithm=self.algorithms[0])
        decoded_payload = decode_and_validate_jwt(expired_token, self.secret_key, self.algorithms)
        self.assertIsNone(decoded_payload)

    def test_invalid_jwt(self):
        # 测试无效的 JWT
        invalid_token = self.token + 'invalid_part'
        decoded_payload = decode_and_validate_jwt(invalid_token, self.secret_key, self.algorithms)
        self.assertIsNone(decoded_payload)

if __name__ == '__main__':
    unittest.main()
