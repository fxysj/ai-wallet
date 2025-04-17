from enum import Enum
import uuid
from typing import Dict, List, Optional


class TransactionStatus(Enum):
    STARTED = "STARTED"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"


class LLMTransaction:
    def __init__(self):
        self.transaction_id = str(uuid.uuid4())
        self.status = TransactionStatus.STARTED
        self.operations: List[dict] = []
        self.compensation_operations: List[dict] = []

    def add_operation(self, operation: dict, compensation: dict):
        self.operations.append(operation)
        self.compensation_operations.append(compensation)

    def commit(self):
        self.status = TransactionStatus.COMMITTED

    def rollback(self):
        self.status = TransactionStatus.ROLLED_BACK
        for comp_op in reversed(self.compensation_operations):
            try:
                # Execute compensation logic
                pass
            except Exception as e:
                self.status = TransactionStatus.FAILED
                raise e