class BusinessException(Exception):
    def __init__(self, code: int = 4000, msg: str = "业务异常"):
        self.code = code
        self.msg = msg

class ModelOutputException(Exception):
    def __init__(self, detail: str = "模型输出格式错误"):
        self.detail = detail
