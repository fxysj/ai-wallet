import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any

@dataclass
class LLMMetric:
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency: float
    timestamp: datetime
    status: str
    cost: float

class LLMTelemetry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMTelemetry, cls).__new__(cls)
            cls._instance.metrics = []
        return cls._instance

    def record_metric(self, metric: LLMMetric):
        self.metrics.append(metric)

    def get_metrics(self) -> List[LLMMetric]:
        return self.metrics