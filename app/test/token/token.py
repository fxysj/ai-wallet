token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJFdm1BZGRyZXNzIjoiMHg5ODBkZDFjMjc2MTQxMjEyMzFmNWE2NGRiOWRkN2M2NzljMzU1MWQyIiwiU29sYW5hQWRkcmVzcyI6IjhRQUtyZzlqSFZlTXJRajFaS0RQdnp6cU5NNWRobWRYVGhmdUFwY3lrbzZhIiwiVHJvbkFkZHJlc3MiOiJURnJWbnExQ2NyakJnYUZCdlAyaUx5a0pRUTZhb1o5SGY0IiwidXNlcl9pZCI6InRlc3RfYWNjb3VudCJ9.LGYIEsiTsNXLkepao365smkvMGECUERuyVLZx6xNly0"
SECRET_KEY = "fibonacci_blx2024_be_with_you"
ALGORITHM = "HS256"
if __name__ == '__main__':
    from app.agents.toolsUtils.jwt_utils import  decode_and_validate_jwt
    response = decode_and_validate_jwt(token=token,secret_key=SECRET_KEY,algorithms=[ALGORITHM])
    print(response)

