"""Weather Schemas for Stadium Commander.

This module defines the structured data representations (schemas) used to transfer
telemetry inputs and analysis results for stadium weather conditions.

Purpose:
    Enforce data validation, strong typing, and schema correctness for weather inputs,
    predictions, and responses.

Inputs:
    - WeatherInput: Current telemetry for temperature, rain, wind, lightning, visibility,
      and match phase.

Outputs:
    - WeatherResponse: Evaluated operational risks, predictions, and detailed reasoning.
    - WeatherPrediction: Forecast of operational impacts, delays, and action recommendations.

Deterministic Guarantees:
    - This schema enforces strict data boundary checks (e.g., temperature range,
      non-negative wind/visibility, probability bounds).
    - Ensures structural validity of all weather-related JSON packages.

AI Usage:
    - All validation rules, schemas, and enums in this module are strictly code-defined
      and executed deterministically. No LLM or generative AI is used for validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from models.common import RiskLevel, MatchPhase



class WeatherPrediction(BaseModel):
    """Prediction model for weather operational impacts, delays, and recommendations."""
    expected_operational_impact: str = Field(
        ...,
        description="Text description of the predicted operational impact."
    )
    expected_delay_minutes: int = Field(
        ...,
        ge=0,
        description="Predicted delay in minutes due to weather conditions."
    )
    recommendation: str = Field(
        ...,
        description="Specific recommended action for stadium operations."
    )


class WeatherInput(BaseModel):
    """Input model containing current weather telemetry."""
    temperature_celsius: Optional[float] = Field(
        None,
        ge=-30.0,
        le=60.0,
        description="Current ambient temperature in degrees Celsius (must be between -30 and 60)."
    )
    rain_probability: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Probability of rain as a percentage (must be between 0 and 100)."
    )
    wind_speed_kmh: Optional[float] = Field(
        None,
        ge=0.0,
        description="Current wind speed in kilometers per hour (must be >= 0)."
    )
    lightning_detected: Optional[bool] = Field(
        None,
        description="True if lightning is detected in the stadium vicinity."
    )
    visibility_meters: Optional[float] = Field(
        None,
        ge=0.0,
        description="Horizontal visibility range in meters (must be >= 0)."
    )
    match_phase: Optional[MatchPhase] = Field(
        None,
        description="The phase of the match (e.g., MatchPhase.T_120, MatchPhase.RAIN_EVENT)."
    )


class WeatherResponse(BaseModel):
    """Structured response output for the weather operations report."""
    risk: RiskLevel = Field(
        ...,
        description="Overall weather operational risk level."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score decimal (0.0-1.0) based on data completeness."
    )
    weather_status: RiskLevel = Field(
        ...,
        description="Detailed weather risk status level."
    )
    prediction: WeatherPrediction = Field(
        ...,
        description="Predicted operational impact, delay, and action recommendation."
    )
    reasoning: List[str] = Field(
        ...,
        description="Step-by-step reasoning explaining every operational decision."
    )
