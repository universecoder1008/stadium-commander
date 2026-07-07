from pydantic import BaseModel
from typing import List


class GateData(BaseModel):
    gate: str
    occupancy: int
    queue_minutes: int
    entry_rate: int


class ParkingData(BaseModel):
    occupancy: int
    available_spots: int


class MetroData(BaseModel):
    next_arrival_minutes: int
    expected_passengers: int


class BusData(BaseModel):
    delay_minutes: int


class TransportData(BaseModel):
    parking: ParkingData
    metro: MetroData
    bus: BusData


class StadiumInput(BaseModel):
    current_time: str
    match_phase: str
    gates: List[GateData]
    transport: TransportData