"""Stadium Input schemas for Stadium Commander.

This module defines the models representing the raw telemetry received at the platform endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from models.transport_schema import TransportInput
from models.medical_schema import MedicalInput
from models.weather_schema import WeatherInput
from models.volunteer_schema import VolunteerInput


class GateData(BaseModel):
    """Telemetry data for individual stadium gates."""
    gate: str = Field(..., description="Unique name/identifier of the gate")
    occupancy: int = Field(..., ge=0, le=100, description="Current queue occupancy percentage")
    queue_minutes: int = Field(..., ge=0, description="Estimated waiting queue duration in minutes")
    entry_rate: int = Field(..., ge=0, description="Rate of ticket scans/entries per minute")


class ParkingData(BaseModel):
    """Telemetry data for physical parking segments."""
    occupancy: int = Field(..., ge=0, description="Number of occupied vehicle spaces")
    available_spots: int = Field(..., ge=0, description="Number of vacant vehicle spaces")


class MetroData(BaseModel):
    """Telemetry data for transit link arrivals."""
    next_arrival_minutes: int = Field(..., ge=0, description="Time until the next metro train arrives in minutes")
    expected_passengers: int = Field(..., ge=0, description="Expected passenger volume on the next arrival")


class BusData(BaseModel):
    """Telemetry data for shuttle bus queues."""
    delay_minutes: int = Field(..., ge=0, description="Average shuttle transit delay in minutes")


class TransportData(BaseModel):
    """Aggregated operational transit telemetry."""
    parking: ParkingData = Field(..., description="Parking lot telemetry details")
    metro: MetroData = Field(..., description="Metro station link details")
    bus: BusData = Field(..., description="Shuttle bus transit details")


class StadiumInput(BaseModel):
    """Combined platform telemetry package received at simulator endpoints."""
    current_time: str = Field(..., description="System timestamp representation")
    match_phase: str = Field(..., description="Current status phase on the event timeline")
    gates: List[GateData] = Field(..., description="Telemetry logs for all active stadium gates")
    transport: TransportData = Field(..., description="General transport logistics metrics")

    # Optional sub-inputs for individual analyzers
    transport_telemetry: Optional[TransportInput] = None
    medical: Optional[MedicalInput] = None
    weather: Optional[WeatherInput] = None
    volunteer: Optional[VolunteerInput] = None