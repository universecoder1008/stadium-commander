"""Volunteer Schemas for Stadium Commander.

This module defines the structured data representations (schemas) used to transfer
telemetry inputs and analysis results for stadium volunteer coordination.

Purpose:
    Enforce data validation, strong typing, and schema correctness for volunteer inputs,
    predictions, and responses.

Inputs:
    - VolunteerInput: Current telemetry for available/total volunteers, zone assignments,
      coverage, response times, active requests, and match phase.

Outputs:
    - VolunteerResponse: Evaluated operational risks, predictions, and detailed reasoning.
    - VolunteerPrediction: Forecast of volunteer shortages, response times, and redeployments.

Deterministic Guarantees:
    - This schema enforces strict data boundary checks (e.g., non-negative counts,
      coverage percentage limits, available resources bounded by total resources).
    - Ensures structural validity of all volunteer-related JSON packages.

AI Usage:
    - All validation rules, schemas, and enums in this module are strictly code-defined
      and executed deterministically. No LLM or generative AI is used for validation.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, model_validator
from models.common import RiskLevel, MatchPhase


class VolunteerPrediction(BaseModel):
    """Prediction regarding expected shortages, response times, and recommended redeployments."""
    expected_shortage: int = Field(
        ...,
        ge=0,
        description="Predicted shortage in volunteer headcounts."
    )
    recommended_redeployment: str = Field(
        ...,
        description="Recommended shift or redeployment directions."
    )
    predicted_response_time: float = Field(
        ...,
        ge=0.0,
        description="Estimated average response time in minutes under predicted load."
    )


class VolunteerInput(BaseModel):
    """Input model containing current volunteer coordination telemetry."""
    available_volunteers: Optional[int] = Field(
        None,
        ge=0,
        description="Number of currently unassigned/available volunteers."
    )
    total_volunteers: Optional[int] = Field(
        None,
        ge=0,
        description="Total number of volunteers deployed."
    )
    zone_assignments: Optional[Dict[str, int]] = Field(
        None,
        description="Mapping of zone identifiers to currently active volunteer counts."
    )
    zone_coverage_percent: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Current average zone coverage as a percentage."
    )
    average_response_time_minutes: Optional[float] = Field(
        None,
        ge=0.0,
        description="Average response time in minutes for volunteer dispatches."
    )
    active_requests: Optional[int] = Field(
        None,
        ge=0,
        description="Number of active operational requests requiring volunteers."
    )
    match_phase: Optional[MatchPhase] = Field(
        None,
        description="The phase of the match (e.g., MatchPhase.T_120, MatchPhase.RAIN_EVENT)."
    )

    @model_validator(mode="after")
    def validate_bounds(self) -> "VolunteerInput":
        """Validates that logical limits are respected in the telemetry dataset."""
        if self.total_volunteers is not None and self.available_volunteers is not None:
            if self.available_volunteers > self.total_volunteers:
                raise ValueError("available_volunteers cannot exceed total_volunteers")
        return self


class VolunteerResponse(BaseModel):
    """Structured response output for the volunteer coordination report."""
    risk: RiskLevel = Field(
        ...,
        description="Overall volunteer operational risk level."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score percentage based on data completeness."
    )
    volunteer_utilization_percent: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Calculated volunteer utilization as a percentage."
    )
    coverage_percent: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Assigned zone coverage percentage."
    )
    prediction: VolunteerPrediction = Field(
        ...,
        description="Predicted operational shortage and redeployment action."
    )
    reasoning: List[str] = Field(
        ...,
        description="Step-by-step reasoning explaining every operational decision."
    )
