"""Commander Schemas for Stadium Commander.

This module defines the structured data representations (schemas) used to transfer
reasoning results from the Commander Agent (Gemini).
"""

from typing import List
from pydantic import BaseModel, Field


class CommanderResponse(BaseModel):
    """Aggregated reasoning response from the Chief Operating Officer Commander Agent."""
    priority: str = Field(
        ...,
        description="Unified risk priority level (LOW, MEDIUM, HIGH, CRITICAL)."
    )
    top_risk: str = Field(
        ...,
        description="Primary critical risk identified across all reports."
    )
    summary: str = Field(
        ...,
        description="Text summary of the overall stadium status."
    )
    actions: List[str] = Field(
        ...,
        description="List of immediate recommended operational actions."
    )
    estimated_impact: str = Field(
        ...,
        description="Predicted operational outcome/impact of recommended actions."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall reasoning confidence value from 0.0 to 1.0."
    )