"""Transport Schemas for Stadium Commander.

This module defines the structured data representations (schemas) used to transfer
telemetry inputs and analysis results for stadium transport logistics.

Purpose:
    Enforce data validation, strong typing, and schema correctness for transport inputs,
    predictions, and responses.

Inputs:
    - TransportInput: Current telemetry for stadium parking, metro, and bus transit.

Outputs:
    - TransportResponse: Evaluated operational risks, predictions, and detailed reasoning.
    - TransportPrediction: Forecast of remaining spectators and transit clearance times.

Deterministic Guarantees:
    - This schema enforces strict data boundary checks (e.g. non-negative counts, occupancy Limits).
    - Ensures structural validity of all transport-related JSON packages.

AI Usage:
    - All validation rules, schemas, and enums in this module are strictly code-defined
      and executed deterministically. No LLM or generative AI is used for validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from models.common import RiskLevel, MatchPhase




class TransportPrediction(BaseModel):
    """Prediction regarding remaining spectators and expected arrival times."""
    remaining_spectators: int = Field(
        ...,
        ge=0,
        description="Predicted number of incoming spectators still to arrive."
    )
    estimated_arrival_minutes: int = Field(
        ...,
        ge=0,
        description="Estimated duration in minutes for remaining spectators to arrive, including delays."
    )


class TransportInput(BaseModel):
    """Input model containing current transportation telemetry."""
    parking_capacity: Optional[int] = Field(
        None,
        ge=0,
        description="Total parking spaces capacity at the stadium."
    )
    parking_occupied: Optional[int] = Field(
        None,
        ge=0,
        description="Number of currently occupied parking spaces."
    )
    metro_expected: Optional[int] = Field(
        None,
        ge=0,
        description="Total expected spectators arriving via metro transit."
    )
    metro_arrived: Optional[int] = Field(
        None,
        ge=0,
        description="Total spectators who have already arrived via metro transit."
    )
    metro_delay_minutes: Optional[int] = Field(
        None,
        ge=0,
        description="Current metro delays in minutes."
    )
    buses_expected: Optional[int] = Field(
        None,
        ge=0,
        description="Total expected spectators arriving via bus transit."
    )
    buses_arrived: Optional[int] = Field(
        None,
        ge=0,
        description="Total spectators who have already arrived via bus transit."
    )
    bus_delay_minutes: Optional[int] = Field(
        None,
        ge=0,
        description="Current bus delays in minutes."
    )
    match_phase: Optional[MatchPhase] = Field(
        None,
        description="The phase of the match (e.g., MatchPhase.T_120, MatchPhase.KICKOFF)."
    )

    @model_validator(mode="after")
    def validate_inputs(self) -> "TransportInput":
        """Validate parking occupancy, metro arrivals, and bus arrivals.

        Ensures that actual arrived or occupied quantities do not exceed their
        respective capacities or expected limits.
        """
        if self.parking_capacity is not None and self.parking_occupied is not None:
            if self.parking_occupied > self.parking_capacity:
                raise ValueError("parking_occupied cannot exceed parking_capacity")

        if self.metro_expected is not None and self.metro_arrived is not None:
            if self.metro_arrived > self.metro_expected:
                raise ValueError("metro_arrived cannot exceed metro_expected")

        if self.buses_expected is not None and self.buses_arrived is not None:
            if self.buses_arrived > self.buses_expected:
                raise ValueError("buses_arrived cannot exceed buses_expected")

        return self
        

class TransportResponse(BaseModel):
    """Structured response output for the transport operations report."""
    risk: RiskLevel = Field(
        ...,
        description="Overall transport operational risk level."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score decimal (0.0-1.0) based on data completeness."
    )
    parking_occupancy_percent: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Calculated parking occupancy percentage."
    )
    metro_status: RiskLevel = Field(
        ...,
        description="Calculated risk status level for metro transit."
    )
    bus_status: RiskLevel = Field(
        ...,
        description="Calculated risk status level for bus transit."
    )
    arrival_prediction: TransportPrediction = Field(
        ...,
        description="Predicted spectator flow arrival details."
    )
    reasoning: List[str] = Field(
        ...,
        description="Step-by-step reasoning explaining every operational decision."
    )