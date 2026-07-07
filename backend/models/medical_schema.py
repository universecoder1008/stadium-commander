"""Medical Schemas for Stadium Commander.

This module defines the structured data representations (schemas) used to transfer
telemetry inputs and analysis results for stadium medical operations.

Purpose:
    Enforce data validation, strong typing, and schema correctness for medical inputs,
    predictions, and responses.

Inputs:
    - MedicalInput: Current telemetry for stadium incidents, queues, and emergency resources.

Outputs:
    - MedicalResponse: Evaluated operational risks, predictions, and detailed reasoning.
    - MedicalPrediction: Forecast of future incidents, resource shortages, and response times.

Deterministic Guarantees:
    - This schema enforces strict data boundary checks (e.g., non-negative counts,
      available resources bounded by total resources).
    - Ensures structural validity of all medical-related JSON packages.

AI Usage:
    - All validation rules, schemas, and enums in this module are strictly code-defined
      and executed deterministically. No LLM or generative AI is used for validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from models.transport_schema import RiskLevel, MatchPhase


class MedicalPrediction(BaseModel):
    """Prediction regarding future incidents, resource shortages, and estimated response time."""
    predicted_incidents: int = Field(
        ...,
        ge=0,
        description="Deterministic forecast of future incidents."
    )
    resource_shortage: bool = Field(
        ...,
        description="True if a shortage of medical staff or ambulances is expected."
    )
    estimated_response_time: int = Field(
        ...,
        ge=0,
        description="Estimated average response time in minutes under current load."
    )


class MedicalInput(BaseModel):
    """Input model containing current medical operations telemetry."""
    active_incidents: Optional[int] = Field(
        None,
        ge=0,
        description="Number of currently active medical incidents."
    )
    critical_incidents: Optional[int] = Field(
        None,
        ge=0,
        description="Number of currently critical/severe incidents."
    )
    ambulances_available: Optional[int] = Field(
        None,
        ge=0,
        description="Number of currently available ambulances."
    )
    ambulances_total: Optional[int] = Field(
        None,
        ge=0,
        description="Total number of ambulances deployed."
    )
    first_aid_queue: Optional[int] = Field(
        None,
        ge=0,
        description="Number of people waiting in first aid queues."
    )
    medical_staff_available: Optional[int] = Field(
        None,
        ge=0,
        description="Number of currently available medical staff members."
    )
    medical_staff_total: Optional[int] = Field(
        None,
        ge=0,
        description="Total number of medical staff members deployed."
    )
    average_response_time_minutes: Optional[int] = Field(
        None,
        ge=0,
        description="Current average dispatch/response time in minutes."
    )
    match_phase: Optional[MatchPhase] = Field(
        None,
        description="The phase of the match (e.g., MatchPhase.T_120, MatchPhase.RAIN_EVENT)."
    )

    @model_validator(mode="after")
    def validate_bounds(self) -> "MedicalInput":
        """Validates that logical limits are respected in the telemetry dataset."""
        if self.active_incidents is not None and self.critical_incidents is not None:
            if self.critical_incidents > self.active_incidents:
                raise ValueError("critical_incidents cannot exceed active_incidents")

        if self.ambulances_total is not None and self.ambulances_available is not None:
            if self.ambulances_available > self.ambulances_total:
                raise ValueError("ambulances_available cannot exceed ambulances_total")

        if self.medical_staff_total is not None and self.medical_staff_available is not None:
            if self.medical_staff_available > self.medical_staff_total:
                raise ValueError("medical_staff_available cannot exceed medical_staff_total")

        return self


class MedicalResponse(BaseModel):
    """Structured response output for the medical operations report."""
    risk: RiskLevel = Field(
        ...,
        description="Overall medical operational risk level."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score percentage based on data completeness."
    )
    ambulance_utilization_percent: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Calculated ambulance utilization as a percentage."
    )
    medical_staff_utilization_percent: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Calculated medical staff utilization as a percentage."
    )
    prediction: MedicalPrediction = Field(
        ...,
        description="Predicted incident volume and resource constraints."
    )
    reasoning: List[str] = Field(
        ...,
        description="Step-by-step reasoning explaining every operational decision."
    )
