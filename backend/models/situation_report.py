"""Situation Report Schema for Stadium Commander.

This module defines the schema representation for the CombinedSituationReport,
which aggregates the results from all individual operational analyzers.

Purpose:
    Enforce data validation and structure for the consolidated report sent to
    the Commander Agent (Gemini).

Deterministic Guarantees:
    - Overall system status calculation is strictly code-defined based on component
      risk levels.
"""

from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from models.crowd_schema import CrowdResponse
from models.transport_schema import TransportResponse
from models.medical_schema import MedicalResponse
from models.weather_schema import WeatherResponse
from models.volunteer_schema import VolunteerResponse


class SystemStatus(str, Enum):
    """System-wide operational risk status levels."""
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class CombinedSituationReport(BaseModel):
    """Aggregated operational report containing telemetry analysis from all subsystems."""
    timestamp: str = Field(
        ...,
        description="Current simulation time or timestamp string."
    )
    match_phase: str = Field(
        ...,
        description="The active phase of the match timeline."
    )
    crowd: Optional[CrowdResponse] = Field(
        None,
        description="Crowd analyzer result."
    )
    transport: Optional[TransportResponse] = Field(
        None,
        description="Transport analyzer result."
    )
    medical: Optional[MedicalResponse] = Field(
        None,
        description="Medical analyzer result."
    )
    weather: Optional[WeatherResponse] = Field(
        None,
        description="Weather analyzer result."
    )
    volunteer: Optional[VolunteerResponse] = Field(
        None,
        description="Volunteer analyzer result."
    )
    system_status: SystemStatus = Field(
        ...,
        description="Calculated system-wide status level (NORMAL, WARNING, CRITICAL)."
    )
    version: str = Field(
        "1.0.0",
        description="Report format version."
    )
    analyzers_completed: List[str] = Field(
        ...,
        description="List of analyzer names that completed execution successfully."
    )
    analyzers_failed: Dict[str, str] = Field(
        ...,
        description="Dictionary mapping failed analyzer names to their exception messages."
    )
    processing_time_ms: float = Field(
        ...,
        description="Total orchestrator analysis duration in milliseconds."
    )
