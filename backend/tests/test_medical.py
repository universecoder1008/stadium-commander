"""Unit tests for the Stadium Commander Medical Analyzer.

Purpose:
    Verify the correctness of schema validations, deterministic risk analysis rules,
    utilization formulas, incident forecasting predictions, confidence scores,
    and timeline-based medical simulator outputs.

Inputs:
    - MedicalInput telemetry datasets (valid/invalid combinations).
    - MatchPhase enum values and simulator configurations.

Outputs:
    - Validation success/error assertions, correct risk status assertions,
      correct spectator medical predictions, and simulator phase matches.

Deterministic Guarantees:
    - All tests verify deterministic mappings. No random variables are checked.
    - Tests assert exact float, integer, and enum match expectations.

AI Usage:
    - This testing module is entirely code-defined. No generative AI or LLMs are used
      for evaluating or asserting test outcomes.
"""

import pytest
from pydantic import ValidationError

from models.transport_schema import RiskLevel, MatchPhase
from models.medical_schema import MedicalInput
from analyzers.medical_analyzer import MedicalAnalyzer
from simulator.medical_simulator import MedicalSimulator


# ----------------------------------------------------------------------
# Schema Validation Tests
# ----------------------------------------------------------------------

def test_medical_input_validation():
    """Verify that field values, bounds, and cross-field relationships validate correctly."""
    # Valid input with proper enum values
    valid_input = MedicalInput(
        active_incidents=5,
        critical_incidents=2,
        ambulances_available=8,
        ambulances_total=10,
        first_aid_queue=3,
        medical_staff_available=45,
        medical_staff_total=50,
        average_response_time_minutes=2,
        match_phase=MatchPhase.T_90
    )
    assert valid_input.critical_incidents == 2
    assert valid_input.match_phase == MatchPhase.T_90

    # Negative values should fail validation
    with pytest.raises(ValidationError):
        MedicalInput(active_incidents=-1)

    # critical_incidents > active_incidents should fail validation
    with pytest.raises(ValidationError):
        MedicalInput(active_incidents=5, critical_incidents=6)

    # ambulances_available > ambulances_total should fail validation
    with pytest.raises(ValidationError):
        MedicalInput(ambulances_available=6, ambulances_total=5)

    # medical_staff_available > medical_staff_total should fail validation
    with pytest.raises(ValidationError):
        MedicalInput(medical_staff_available=51, medical_staff_total=50)


# ----------------------------------------------------------------------
# Analyzer Tests
# ----------------------------------------------------------------------

@pytest.fixture
def analyzer():
    return MedicalAnalyzer()


def test_ambulance_utilization(analyzer):
    """Verify ambulance utilization calculations and risk mapping."""
    # 0% utilization -> LOW risk (10 available of 10 total)
    res_low = analyzer.analyze(MedicalInput(ambulances_available=10, ambulances_total=10))
    assert res_low.ambulance_utilization_percent == 0.0
    assert res_low.risk == RiskLevel.LOW

    # 50% utilization -> MEDIUM risk (5 available of 10 total)
    res_med = analyzer.analyze(MedicalInput(ambulances_available=5, ambulances_total=10))
    assert res_med.ambulance_utilization_percent == 50.0
    # Overall risk is MEDIUM because one metric is MEDIUM
    assert res_med.risk == RiskLevel.MEDIUM

    # 90% utilization -> HIGH risk (1 available of 10 total)
    res_high = analyzer.analyze(MedicalInput(ambulances_available=1, ambulances_total=10))
    assert res_high.ambulance_utilization_percent == 90.0
    # Overall risk is HIGH because one metric is HIGH
    assert res_high.risk == RiskLevel.HIGH


def test_staff_utilization(analyzer):
    """Verify medical staff utilization calculations and risk mapping."""
    # 20% utilization -> LOW risk (40 available of 50 total)
    res_low = analyzer.analyze(MedicalInput(medical_staff_available=40, medical_staff_total=50))
    assert res_low.medical_staff_utilization_percent == 20.0
    assert res_low.risk == RiskLevel.LOW

    # 60% utilization -> MEDIUM risk (20 available of 50 total)
    res_med = analyzer.analyze(MedicalInput(medical_staff_available=20, medical_staff_total=50))
    assert res_med.medical_staff_utilization_percent == 60.0
    assert res_med.risk == RiskLevel.MEDIUM

    # 84% utilization -> HIGH risk (8 available of 50 total)
    res_high = analyzer.analyze(MedicalInput(medical_staff_available=8, medical_staff_total=50))
    assert res_high.medical_staff_utilization_percent == 84.0
    assert res_high.risk == RiskLevel.HIGH


def test_queue_risk(analyzer):
    """Verify queue size risk thresholds (<5 LOW, 5-15 MEDIUM, >15 HIGH)."""
    # 4 -> LOW
    assert analyzer.analyze(MedicalInput(first_aid_queue=4)).risk == RiskLevel.LOW
    # 5 -> MEDIUM
    assert analyzer.analyze(MedicalInput(first_aid_queue=5)).risk == RiskLevel.MEDIUM
    # 15 -> MEDIUM
    assert analyzer.analyze(MedicalInput(first_aid_queue=15)).risk == RiskLevel.MEDIUM
    # 16 -> HIGH
    assert analyzer.analyze(MedicalInput(first_aid_queue=16)).risk == RiskLevel.HIGH


def test_response_time_risk(analyzer):
    """Verify average response time risk thresholds (<3 LOW, 3-8 MEDIUM, >8 HIGH)."""
    # 2 -> LOW
    assert analyzer.analyze(MedicalInput(average_response_time_minutes=2)).risk == RiskLevel.LOW
    # 3 -> MEDIUM
    assert analyzer.analyze(MedicalInput(average_response_time_minutes=3)).risk == RiskLevel.MEDIUM
    # 8 -> MEDIUM
    assert analyzer.analyze(MedicalInput(average_response_time_minutes=8)).risk == RiskLevel.MEDIUM
    # 9 -> HIGH
    assert analyzer.analyze(MedicalInput(average_response_time_minutes=9)).risk == RiskLevel.HIGH


def test_critical_incidents_escalation(analyzer):
    """Verify risk escalation when critical incidents are present."""
    # Base risk is LOW (all inputs low risk). Critical incidents = 1.
    # LOW risk escalated -> MEDIUM.
    inp_low = MedicalInput(
        active_incidents=1, critical_incidents=1,
        first_aid_queue=2, average_response_time_minutes=1
    )
    res_low = analyzer.analyze(inp_low)
    assert res_low.risk == RiskLevel.MEDIUM

    # Base risk is MEDIUM (queue is 6). Critical incidents = 1.
    # MEDIUM risk escalated -> HIGH.
    inp_med = MedicalInput(
        active_incidents=2, critical_incidents=1,
        first_aid_queue=6, average_response_time_minutes=1
    )
    res_med = analyzer.analyze(inp_med)
    assert res_med.risk == RiskLevel.HIGH

    # Base risk is HIGH (queue is 20). Critical incidents = 1.
    # HIGH risk remains HIGH.
    inp_high = MedicalInput(
        active_incidents=5, critical_incidents=1,
        first_aid_queue=20, average_response_time_minutes=1
    )
    res_high = analyzer.analyze(inp_high)
    assert res_high.risk == RiskLevel.HIGH


def test_predictions(analyzer):
    """Verify predictions for future incident rates, resource shortages, and ETA escalations."""
    # Test low activity match phase prediction (T-120)
    # Predicted incidents: active(10) * 1.1 + 1 = 12
    # Est response time: base(2) + 2 (queue 10 is >5) = 4
    inp_t120 = MedicalInput(
        active_incidents=10, critical_incidents=0,
        first_aid_queue=10, average_response_time_minutes=2,
        match_phase=MatchPhase.T_120,
        medical_staff_available=30, medical_staff_total=30,
        ambulances_available=10, ambulances_total=10
    )
    pred_t120 = analyzer.analyze(inp_t120).prediction
    assert pred_t120.predicted_incidents == 12
    assert pred_t120.estimated_response_time == 4
    assert pred_t120.resource_shortage is False

    # Test peak activity match phase prediction (T-30)
    # Predicted incidents: active(10) * 1.5 + 3 = 18
    # Est response time: base(2) + 5 (queue 20 is >15) + 3 (ambulance utilization 90% is >80%) = 10
    inp_t30 = MedicalInput(
        active_incidents=10, critical_incidents=0,
        first_aid_queue=20, average_response_time_minutes=2,
        match_phase=MatchPhase.T_30,
        medical_staff_available=30, medical_staff_total=30,
        ambulances_available=1, ambulances_total=10
    )
    pred_t30 = analyzer.analyze(inp_t30).prediction
    assert pred_t30.predicted_incidents == 18
    assert pred_t30.estimated_response_time == 10
    # Resource shortage should be True because ambulance utilization is 90%
    assert pred_t30.resource_shortage is True


def test_confidence_calculation(analyzer):
    """Verify confidence calculation as a float between 0.0 and 1.0 based on fields completeness."""
    # All 9 fields provided -> 1.0 confidence
    inp_full = MedicalInput(
        active_incidents=5, critical_incidents=1,
        ambulances_available=8, ambulances_total=10,
        first_aid_queue=2, medical_staff_available=40, medical_staff_total=50,
        average_response_time_minutes=3, match_phase=MatchPhase.KICKOFF
    )
    assert analyzer.analyze(inp_full).confidence == 1.0

    # 4 fields provided -> ~0.44 confidence (4 / 9 = 0.4444... rounded to 0.44)
    inp_partial = MedicalInput(
        active_incidents=5, critical_incidents=1,
        ambulances_total=10, match_phase=MatchPhase.KICKOFF
    )
    assert analyzer.analyze(inp_partial).confidence == 0.44

    # 0 fields provided -> 0.0 confidence
    assert analyzer.analyze(MedicalInput()).confidence == 0.0


# ----------------------------------------------------------------------
# Simulator Tests
# ----------------------------------------------------------------------

def test_simulator_phases():
    """Verify simulator generates correct deterministic profiles for MatchPhase values."""
    sim = MedicalSimulator()

    # T-120: low incidents, full resources
    t120 = sim.generate(MatchPhase.T_120)
    assert t120.active_incidents == 1
    assert t120.critical_incidents == 0
    assert t120.ambulances_available == t120.ambulances_total
    assert t120.medical_staff_available == t120.medical_staff_total

    # T-30: heat exhaustion
    t30 = sim.generate(MatchPhase.T_30)
    assert t30.active_incidents == 12
    assert t30.critical_incidents == 2
    assert t30.first_aid_queue == 12

    # Rain Event: slip injuries, high demand
    rain = sim.generate(MatchPhase.RAIN_EVENT)
    assert rain.active_incidents == 18
    assert rain.critical_incidents == 3
    assert rain.first_aid_queue == 22

    # Full-time: highest demand
    full = sim.generate(MatchPhase.FULLTIME)
    assert full.active_incidents == 25
    assert full.critical_incidents == 4
    assert full.ambulances_available == 1
    assert full.first_aid_queue == 30

    # Safe string conversion check
    assert sim.generate("Rain Event").match_phase == MatchPhase.RAIN_EVENT

    # Invalid phase throws ValueError
    with pytest.raises(ValueError):
        sim.generate("UnknownPhase")
