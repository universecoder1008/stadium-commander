"""Unit tests for the Stadium Commander Transport Analyzer.

Purpose:
    Verify the correctness of schema validations, deterministic risk analysis rules,
    arrival predictions, confidence scores, and timeline-based simulator outputs.

Inputs:
    - TransportInput telemetry datasets (valid/invalid combinations).
    - MatchPhase enum values and simulator configurations.

Outputs:
    - Validation success/error assertions, correct risk status assertions,
      correct spectator flow predictions, and simulator phase matches.

Deterministic Guarantees:
    - All tests verify deterministic mappings. No random variables are checked.
    - Tests assert exact float, integer, and enum match expectations.

AI Usage:
    - This testing module is entirely code-defined. No generative AI or LLMs are used
      for evaluating or asserting test outcomes.
"""

import pytest
from pydantic import ValidationError

from models.common import RiskLevel, MatchPhase
from models.transport_schema import TransportInput

from analyzers.transport_analyzer import TransportAnalyzer
from simulator.transport_simulator import TransportSimulator


# ----------------------------------------------------------------------
# Schema Validation Tests
# ----------------------------------------------------------------------

def test_transport_input_validation():
    """Verify that field values, bounds, and cross-field relationships validate correctly."""
    # Valid input with proper enum values
    valid_input = TransportInput(
        parking_capacity=1000,
        parking_occupied=700,
        metro_expected=5000,
        metro_arrived=3000,
        metro_delay_minutes=5,
        buses_expected=100,
        buses_arrived=80,
        bus_delay_minutes=10,
        match_phase=MatchPhase.T_90
    )
    assert valid_input.parking_occupied == 700
    assert valid_input.match_phase == MatchPhase.T_90

    # Negative values should fail validation
    with pytest.raises(ValidationError):
        TransportInput(parking_capacity=-10)

    # occupied > capacity should fail validation
    with pytest.raises(ValidationError):
        TransportInput(parking_capacity=500, parking_occupied=600)

    # metro_arrived > metro_expected should fail validation
    with pytest.raises(ValidationError):
        TransportInput(metro_expected=5000, metro_arrived=6000)

    # buses_arrived > buses_expected should fail validation
    with pytest.raises(ValidationError):
        TransportInput(buses_expected=100, buses_arrived=120)


# ----------------------------------------------------------------------
# Analyzer Tests
# ----------------------------------------------------------------------

@pytest.fixture
def analyzer():
    return TransportAnalyzer()


def test_parking_risk(analyzer):
    """Verify parking risk threshold mapping (<70% LOW, 70-90% MEDIUM, >90% HIGH)."""
    # 69.9% occupancy -> LOW risk
    input_low = TransportInput(parking_capacity=1000, parking_occupied=699)
    res_low = analyzer.analyze(input_low)
    assert res_low.parking_occupancy_percent == 69.9
    assert res_low.risk == RiskLevel.LOW

    # 70% occupancy -> MEDIUM risk
    input_med1 = TransportInput(parking_capacity=1000, parking_occupied=700)
    res_med1 = analyzer.analyze(input_med1)
    assert res_med1.parking_occupancy_percent == 70.0
    assert res_med1.risk == RiskLevel.MEDIUM

    # 90% occupancy -> MEDIUM risk
    input_med2 = TransportInput(parking_capacity=1000, parking_occupied=900)
    res_med2 = analyzer.analyze(input_med2)
    assert res_med2.parking_occupancy_percent == 90.0
    assert res_med2.risk == RiskLevel.MEDIUM

    # 90.1% occupancy -> HIGH risk
    input_high = TransportInput(parking_capacity=1000, parking_occupied=901)
    res_high = analyzer.analyze(input_high)
    assert res_high.parking_occupancy_percent == 90.1
    assert res_high.risk == RiskLevel.HIGH


def test_metro_delay_risk(analyzer):
    """Verify metro delay thresholds (<5m LOW, 5-15m MEDIUM, >15m HIGH)."""
    # 4 minutes -> LOW
    assert analyzer.analyze(TransportInput(metro_delay_minutes=4)).metro_status == RiskLevel.LOW
    
    # 5 minutes -> MEDIUM
    assert analyzer.analyze(TransportInput(metro_delay_minutes=5)).metro_status == RiskLevel.MEDIUM
    
    # 15 minutes -> MEDIUM
    assert analyzer.analyze(TransportInput(metro_delay_minutes=15)).metro_status == RiskLevel.MEDIUM
    
    # 16 minutes -> HIGH
    assert analyzer.analyze(TransportInput(metro_delay_minutes=16)).metro_status == RiskLevel.HIGH


def test_bus_delay_risk(analyzer):
    """Verify bus delay thresholds (<5m LOW, 5-15m MEDIUM, >15m HIGH)."""
    # 4 minutes -> LOW
    assert analyzer.analyze(TransportInput(bus_delay_minutes=4)).bus_status == RiskLevel.LOW
    
    # 5 minutes -> MEDIUM
    assert analyzer.analyze(TransportInput(bus_delay_minutes=5)).bus_status == RiskLevel.MEDIUM
    
    # 15 minutes -> MEDIUM
    assert analyzer.analyze(TransportInput(bus_delay_minutes=15)).bus_status == RiskLevel.MEDIUM
    
    # 16 minutes -> HIGH
    assert analyzer.analyze(TransportInput(bus_delay_minutes=16)).bus_status == RiskLevel.HIGH


def test_overall_risk(analyzer):
    """Verify overall risk assessment priority (HIGH > MEDIUM > LOW)."""
    # All LOW -> LOW
    inp_all_low = TransportInput(
        parking_capacity=1000, parking_occupied=100,
        metro_delay_minutes=0, bus_delay_minutes=0
    )
    assert analyzer.analyze(inp_all_low).risk == RiskLevel.LOW

    # One MEDIUM, others LOW -> MEDIUM
    inp_one_med = TransportInput(
        parking_capacity=1000, parking_occupied=750,  # MEDIUM
        metro_delay_minutes=0, bus_delay_minutes=0   # LOW
    )
    assert analyzer.analyze(inp_one_med).risk == RiskLevel.MEDIUM

    # One HIGH, others MEDIUM -> HIGH (HIGH dominates)
    inp_high_dom = TransportInput(
        parking_capacity=1000, parking_occupied=750,  # MEDIUM
        metro_delay_minutes=20, bus_delay_minutes=5   # HIGH, MEDIUM
    )
    assert analyzer.analyze(inp_high_dom).risk == RiskLevel.HIGH


def test_arrival_prediction(analyzer):
    """Verify arrival predictions calculations for spectator counts and eta."""
    # Spectators remaining: Expected (5000 metro + 1000 bus) - Arrived (3000 metro + 400 bus) = 2600 remaining.
    # Metro has remaining spectators (5000-3000 = 2000), delay is 10.
    # Bus has remaining spectators (1000-400 = 600), delay is 5.
    # Expected ETA = Base transit (15) + max active delay (10) = 25.
    inp1 = TransportInput(
        metro_expected=5000, metro_arrived=3000, metro_delay_minutes=10,
        buses_expected=1000, buses_arrived=400, bus_delay_minutes=5
    )
    pred1 = analyzer.analyze(inp1).arrival_prediction
    assert pred1.remaining_spectators == 2600
    assert pred1.estimated_arrival_minutes == 25

    # If all spectators have arrived, ETA should be 0.
    inp_done = TransportInput(
        metro_expected=5000, metro_arrived=5000, metro_delay_minutes=10,
        buses_expected=1000, buses_arrived=1000, bus_delay_minutes=5
    )
    pred_done = analyzer.analyze(inp_done).arrival_prediction
    assert pred_done.remaining_spectators == 0
    assert pred_done.estimated_arrival_minutes == 0

    # If only one transit type has remaining spectators, only its delay is considered in ETA.
    # Metro remaining: 0 (5000-5000). Bus remaining: 600 (1000-400), delay: 20.
    # Expected ETA = Base transit (15) + bus delay (20) = 35. (Metro delay is ignored as no spectators are waiting for metro).
    inp_bus_only = TransportInput(
        metro_expected=5000, metro_arrived=5000, metro_delay_minutes=10,
        buses_expected=1000, buses_arrived=400, bus_delay_minutes=20
    )
    pred_bus = analyzer.analyze(inp_bus_only).arrival_prediction
    assert pred_bus.remaining_spectators == 600
    assert pred_bus.estimated_arrival_minutes == 35


def test_confidence_calculation(analyzer):
    """Verify confidence updates as float values (0.0-1.0) based on completeness of provided telemetry."""
    # All 9 fields provided -> 1.0 confidence
    inp_full = TransportInput(
        parking_capacity=1000, parking_occupied=500,
        metro_expected=2000, metro_arrived=1000, metro_delay_minutes=0,
        buses_expected=200, buses_arrived=100, bus_delay_minutes=0,
        match_phase=MatchPhase.T_60
    )
    assert analyzer.analyze(inp_full).confidence == 1.0

    # 5 fields provided -> ~0.56 confidence (5 / 9 = 0.5555... rounded to 0.56)
    inp_partial = TransportInput(
        parking_capacity=1000, parking_occupied=500,
        metro_expected=2000, metro_arrived=1000,
        match_phase=MatchPhase.T_60
    )
    assert analyzer.analyze(inp_partial).confidence == 0.56

    # 0 fields provided -> 0.0 confidence
    inp_empty = TransportInput()
    assert analyzer.analyze(inp_empty).confidence == 0.0


# ----------------------------------------------------------------------
# Simulator Tests
# ----------------------------------------------------------------------

def test_simulator_phases():
    """Verify simulator generates correct deterministic outputs for standard MatchPhase values."""
    sim = TransportSimulator()

    # T-120: 10% parking, no delays
    t120 = sim.generate(MatchPhase.T_120)
    assert t120.parking_occupied / t120.parking_capacity == 0.1
    assert t120.metro_delay_minutes == 0
    assert t120.bus_delay_minutes == 0

    # T-30: 90% parking, high delays
    t30 = sim.generate(MatchPhase.T_30)
    assert t30.parking_occupied / t30.parking_capacity == 0.9
    assert t30.metro_delay_minutes == 20
    assert t30.bus_delay_minutes == 18

    # Kickoff: parking full, delays stabilize
    kickoff = sim.generate(MatchPhase.KICKOFF)
    assert kickoff.parking_occupied == kickoff.parking_capacity
    assert kickoff.metro_delay_minutes == 3
    assert kickoff.bus_delay_minutes == 2

    # Halftime: minimal activity
    halftime = sim.generate(MatchPhase.HALFTIME)
    assert halftime.metro_expected == 100
    assert halftime.buses_expected == 50

    # Rain Event: rain delays, surface grid active
    rain = sim.generate(MatchPhase.RAIN_EVENT)
    assert rain.parking_occupied == 950
    assert rain.metro_delay_minutes == 15
    assert rain.bus_delay_minutes == 22

    # Full-time: exit rush
    fulltime = sim.generate(MatchPhase.FULLTIME)
    assert fulltime.metro_expected == 12000
    assert fulltime.buses_expected == 5000
    assert fulltime.metro_delay_minutes == 25
    assert fulltime.bus_delay_minutes == 30

    # String values matching phase representation should also work via safe conversion
    assert sim.generate("T-120").match_phase == MatchPhase.T_120
    assert sim.generate("Rain Event").match_phase == MatchPhase.RAIN_EVENT

    # Unknown phase should raise ValueError
    with pytest.raises(ValueError):
        sim.generate("UnknownPhase")
