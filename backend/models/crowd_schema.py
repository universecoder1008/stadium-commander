"""Crowd Schemas for Stadium Commander.

This module defines the validation models representing predictions and risk analysis 
output payloads for crowd telemetry.
"""

from pydantic import BaseModel, Field
from typing import List


class Prediction(BaseModel):
    """Specific prediction details regarding gate operational bottlenecks."""
    gate: str = Field(..., description="Gate identifier associated with the prediction")
    issue: str = Field(..., description="Description of the identified crowd queue anomaly")
    eta_minutes: int = Field(..., ge=0, description="Estimated duration in minutes for recovery/clearance")


class CrowdResponse(BaseModel):
    """Unified risk evaluation output package from the Crowd Analyzer."""
    risk: str = Field(..., description="Analyzed risk status (LOW, MEDIUM, HIGH, CRITICAL)")
    confidence: int = Field(..., ge=0, le=100, description="Analysis confidence rating percentage (0 to 100)")
    predictions: List[Prediction] = Field(..., description="List of specific gate status forecasts")
    reasoning: List[str] = Field(..., description="Logic bullet points supporting evaluated risk status")