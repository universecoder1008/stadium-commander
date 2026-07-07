from pydantic import BaseModel
from typing import List


class Prediction(BaseModel):
    gate: str
    issue: str
    eta_minutes: int


class CrowdResponse(BaseModel):
    risk: str
    confidence: int
    predictions: List[Prediction]
    reasoning: List[str]