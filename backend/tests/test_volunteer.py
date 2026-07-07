"""Unit tests for the Stadium Commander Volunteer Analyzer.

Purpose:
    Verify the correctness of schema validations, deterministic volunteer risk rules,
    redeployment recommendations, confidence scores, and timeline-based volunteer
    simulator outputs.

Inputs:
    - VolunteerInput telemetry datasets (valid/invalid combinations).
    - MatchPhase enum values and simulator configurations.

Outputs:
    - Validation success/error assertions, correct risk status assertions,
      correct volunteer predictions, and simulator phase matches.

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
from models.volunteer_schema import VolunteerInput
from analyzers.volunteer_analyzer import VolunteerAnalyzer
from simulator.volunteer_simulator import VolunteerSimulator


# ----------------------------------------------------------------------
# Schema Validation Tests
# ----------------------------------------------------------------------

def test_volunteer_input_validation():
    """Verify that field bounds and cross-field constraints validate correctly."""
    # Valid input with proper enum values
    valid_input = VolunteerInput(
        available_volunteers=50,
        total_volunteers=100,
        zone_assignments={"Zone A": 20, "Zone B": 30},
        zone_coverage_percent=85.5,
        average_response_time_minutes=4.2,
        active_requests=5,
        match_phase=MatchPhase.T_90
    )
    assert valid_input.available_volunteers == 50
    assert valid_input.match_phase == MatchPhase.T_90

    # Cross-field check: available_volunteers > total_volunteers should fail
    with pytest.raises(ValidationError):
        VolunteerInput(available_volunteers=101, total_volunteers=100)

    # Coverage bounds check (< 0 should fail)
    with pytest.raises(ValidationError):
        VolunteerInput(zone_coverage_percent=-0.1)

    # Coverage bounds check (> 100 should fail)
    with pytest.raises(ValidationError):
        VolunteerInput(zone_coverage_percent=100.1)

    # Response time check (< 0 should fail)
    with pytest.raises(ValidationError):
        VolunteerInput(average_response_time_minutes=-0.1)

    # Active requests check (< 0 should fail)
    with pytest.raises(ValidationError):
        VolunteerInput(active_requests=-1)


# ----------------------------------------------------------------------
# Analyzer Tests
# ----------------------------------------------------------------------

@pytest.fixture
def analyzer():
    return VolunteerAnalyzer()


def test_coverage_thresholds(analyzer):
    """Verify zone coverage thresholds (<50% HIGH, 50%-80% MEDIUM, >80% LOW)."""
    # 49.9% -> HIGH (Note: Lower coverage means HIGHER risk)
    assert analyzer.analyze(VolunteerInput(zone_coverage_percent=49.9)).risk == RiskLevel.HIGH
    # 50.0% -> MEDIUM
    assert analyzer.analyze(VolunteerInput(zone_coverage_percent=50.0)).risk == RiskLevel.MEDIUM
    # 80.0% -> MEDIUM
    assert analyzer.analyze(VolunteerInput(zone_coverage_percent=80.0)).risk == RiskLevel.MEDIUM
    # 80.1% -> LOW
    assert analyzer.analyze(VolunteerInput(zone_coverage_percent=80.1)).risk == RiskLevel.LOW


def test_response_time_thresholds(analyzer):
    """Verify average response time thresholds (<5m LOW, 5m-15m MEDIUM, >15m HIGH)."""
    # 4.9m -> LOW
    assert analyzer.analyze(VolunteerInput(average_response_time_minutes=4.9)).risk == RiskLevel.LOW
    # 5.0m -> MEDIUM
    assert analyzer.analyze(VolunteerInput(average_response_time_minutes=5.0)).risk == RiskLevel.MEDIUM
    # 15.0m -> MEDIUM
    assert analyzer.analyze(VolunteerInput(average_response_time_minutes=15.0)).risk == RiskLevel.MEDIUM
    # 15.1m -> HIGH
    assert analyzer.analyze(VolunteerInput(average_response_time_minutes=15.1)).risk == RiskLevel.HIGH


def test_utilization_thresholds(analyzer):
    """Verify utilization thresholds (<40% LOW, 40%-80% MEDIUM, >80% HIGH)."""
    # 39% utilization -> LOW risk (61 available of 100 total)
    res_low = analyzer.analyze(VolunteerInput(available_volunteers=61, total_volunteers=100))
    assert res_low.volunteer_utilization_percent == 39.0
    assert res_low.risk == RiskLevel.LOW

    # 40% utilization -> MEDIUM risk (60 available of 100 total)
    res_med = analyzer.analyze(VolunteerInput(available_volunteers=60, total_volunteers=100))
    assert res_med.volunteer_utilization_percent == 40.0
    assert res_med.risk == RiskLevel.MEDIUM

    # 80% utilization -> MEDIUM risk (20 available of 100 total)
    res_med2 = analyzer.analyze(VolunteerInput(available_volunteers=20, total_volunteers=100))
    assert res_med2.volunteer_utilization_percent == 80.0
    assert res_med2.risk == RiskLevel.MEDIUM

    # 81% utilization -> HIGH risk (19 available of 100 total)
    res_high = analyzer.analyze(VolunteerInput(available_volunteers=19, total_volunteers=100))
    assert res_high.volunteer_utilization_percent == 81.0
    assert res_high.risk == RiskLevel.HIGH


def test_request_load_thresholds(analyzer):
    """Verify active requests load thresholds (<10 LOW, 10-30 MEDIUM, >30 HIGH)."""
    # 9 -> LOW
    assert analyzer.analyze(VolunteerInput(active_requests=9)).risk == RiskLevel.LOW
    # 10 -> MEDIUM
    assert analyzer.analyze(VolunteerInput(active_requests=10)).risk == RiskLevel.MEDIUM
    # 30 -> MEDIUM
    assert analyzer.analyze(VolunteerInput(active_requests=30)).risk == RiskLevel.MEDIUM
    # 31 -> HIGH
    assert analyzer.analyze(VolunteerInput(active_requests=31)).risk == RiskLevel.HIGH


def test_overall_risk_precedence(analyzer):
    """Verify overall risk assessment priority (HIGH > MEDIUM > LOW)."""
    # All LOW -> LOW
    inp_all_low = VolunteerInput(
        available_volunteers=90, total_volunteers=100,
        zone_coverage_percent=90.0, average_response_time_minutes=3.0,
        active_requests=5
    )
    assert analyzer.analyze(inp_all_low).risk == RiskLevel.LOW

    # One MEDIUM, others LOW -> MEDIUM
    inp_one_med = VolunteerInput(
        available_volunteers=50, total_volunteers=100,  # MEDIUM utilization
        zone_coverage_percent=90.0, average_response_time_minutes=3.0,
        active_requests=5
    )
    assert analyzer.analyze(inp_one_med).risk == RiskLevel.MEDIUM

    # One HIGH, one MEDIUM -> HIGH (HIGH dominates)
    inp_high_dom = VolunteerInput(
        available_volunteers=50, total_volunteers=100,  # MEDIUM utilization
        zone_coverage_percent=45.0,  # HIGH coverage gap risk
        average_response_time_minutes=3.0, active_requests=5
    )
    assert analyzer.analyze(inp_high_dom).risk == RiskLevel.HIGH


def test_predictions(analyzer):
    """Verify expected shortages, predicted response times, and recommended redeployments."""
    # Test shortage and redeployment under rain event
    inp_rain = VolunteerInput(
        available_volunteers=5, active_requests=10,
        average_response_time_minutes=4.0, match_phase=MatchPhase.RAIN_EVENT
    )
    pred_r = analyzer.analyze(inp_rain).prediction
    # Required = 10 * 2 = 20. Shortage = 20 - 5 = 15.
    assert pred_r.expected_shortage == 15
    assert pred_r.predicted_response_time == 4.0 + (15 * 0.5)
    assert "Move outdoor volunteers indoors" in pred_r.recommended_redeployment

    # Test shortage and redeployment under T-30
    inp_t30 = VolunteerInput(
        available_volunteers=2, active_requests=5,
        average_response_time_minutes=3.0, match_phase=MatchPhase.T_30
    )
    pred_t = analyzer.analyze(inp_t30).prediction
    # Required = 5 * 2 = 10. Shortage = 10 - 2 = 8.
    assert pred_t.expected_shortage == 8
    assert pred_t.predicted_response_time == 3.0 + (8 * 0.5)
    assert "Move 5 volunteers from Zone C to Zone A" in pred_t.recommended_redeployment

    # Test shortage and redeployment under Fulltime
    inp_ft = VolunteerInput(
        available_volunteers=1, active_requests=4,
        average_response_time_minutes=2.0, match_phase=MatchPhase.FULLTIME
    )
    pred_f = analyzer.analyze(inp_ft).prediction
    assert "Deploy reserve volunteers to main exits" in pred_f.recommended_redeployment

    # Test no shortage
    inp_clear = VolunteerInput(
        available_volunteers=10, active_requests=2,
        average_response_time_minutes=3.0, match_phase=MatchPhase.KICKOFF
    )
    pred_c = analyzer.analyze(inp_clear).prediction
    assert pred_c.expected_shortage == 0
    assert pred_c.predicted_response_time == 3.0
    assert "Proceed with current zone allocations" in pred_c.recommended_redeployment


def test_confidence_calculation(analyzer):
    """Verify confidence updates as float values (0.0-1.0) based on completeness of provided telemetry."""
    # All 7 fields provided -> 1.0 confidence
    inp_full = VolunteerInput(
        available_volunteers=80, total_volunteers=100,
        zone_assignments={"Zone A": 20}, zone_coverage_percent=85.0,
        average_response_time_minutes=3.0, active_requests=4,
        match_phase=MatchPhase.T_120
    )
    assert analyzer.analyze(inp_full).confidence == 1.0

    # 4 fields provided -> 0.57 confidence (4 / 7 = 0.57)
    inp_partial = VolunteerInput(
        available_volunteers=80,
        total_volunteers=100,
        active_requests=4,
        match_phase=MatchPhase.T_120
    )
    assert analyzer.analyze(inp_partial).confidence == 0.57

    # 0 fields provided -> 0.0 confidence
    assert analyzer.analyze(VolunteerInput()).confidence == 0.0


# ----------------------------------------------------------------------
# Simulator Tests
# ----------------------------------------------------------------------

def test_simulator_phases():
    """Verify simulator generates correct deterministic profiles for MatchPhase values."""
    sim = VolunteerSimulator()

    # T-120: High availability, minimal requests, full coverage
    t120 = sim.generate(MatchPhase.T_120)
    assert t120.available_volunteers == 90
    assert t120.active_requests == 2
    assert t120.zone_coverage_percent == 95.0

    # Rain Event: High workload, low coverage, high response time
    rain = sim.generate(MatchPhase.RAIN_EVENT)
    assert rain.available_volunteers == 10
    assert rain.active_requests == 35
    assert rain.average_response_time_minutes == 16.0

    # Full-time: Exit management
    full = sim.generate(MatchPhase.FULLTIME)
    assert full.available_volunteers == 5
    assert full.active_requests == 40

    # Safe string conversion check
    assert sim.generate("Rain Event").match_phase == MatchPhase.RAIN_EVENT

    # Invalid phase throws ValueError
    with pytest.raises(ValueError):
        sim.generate("UnknownPhase")
