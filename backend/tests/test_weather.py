"""Unit tests for the Stadium Commander Weather Analyzer.

Purpose:
    Verify the correctness of schema validations, deterministic weather risk rules,
    lightning overrides, operational delay predictions, confidence scores,
    and timeline-based weather simulator outputs.

Inputs:
    - WeatherInput telemetry datasets (valid/invalid combinations).
    - MatchPhase enum values and simulator configurations.

Outputs:
    - Validation success/error assertions, correct risk status assertions,
      correct spectator weather predictions, and simulator phase matches.

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

from models.weather_schema import WeatherInput
from analyzers.weather_analyzer import WeatherAnalyzer
from simulator.weather_simulator import WeatherSimulator


# ----------------------------------------------------------------------
# Schema Validation Tests
# ----------------------------------------------------------------------

def test_weather_input_validation():
    """Verify that field bounds and types validate correctly in the schema."""
    # Valid input with proper enum values and floats
    valid_input = WeatherInput(
        temperature_celsius=25.5,
        rain_probability=45.0,
        wind_speed_kmh=20.0,
        lightning_detected=False,
        visibility_meters=8000.0,
        match_phase=MatchPhase.T_90
    )
    assert valid_input.temperature_celsius == 25.5
    assert valid_input.match_phase == MatchPhase.T_90

    # Temperature bounds check (< -30 should fail)
    with pytest.raises(ValidationError):
        WeatherInput(temperature_celsius=-30.1)

    # Temperature bounds check (> 60 should fail)
    with pytest.raises(ValidationError):
        WeatherInput(temperature_celsius=60.1)

    # Rain probability check (< 0 should fail)
    with pytest.raises(ValidationError):
        WeatherInput(rain_probability=-0.1)

    # Rain probability check (> 100 should fail)
    with pytest.raises(ValidationError):
        WeatherInput(rain_probability=100.1)

    # Wind speed check (< 0 should fail)
    with pytest.raises(ValidationError):
        WeatherInput(wind_speed_kmh=-0.1)

    # Visibility check (< 0 should fail)
    with pytest.raises(ValidationError):
        WeatherInput(visibility_meters=-0.1)


# ----------------------------------------------------------------------
# Analyzer Tests
# ----------------------------------------------------------------------

@pytest.fixture
def analyzer():
    return WeatherAnalyzer()


def test_rain_thresholds(analyzer):
    """Verify rain probability thresholds (<30% LOW, 30%-70% MEDIUM, >70% HIGH)."""
    # 29.9% -> LOW
    assert analyzer.analyze(WeatherInput(rain_probability=29.9)).risk == RiskLevel.LOW
    # 30% -> MEDIUM
    assert analyzer.analyze(WeatherInput(rain_probability=30.0)).risk == RiskLevel.MEDIUM
    # 70% -> MEDIUM
    assert analyzer.analyze(WeatherInput(rain_probability=70.0)).risk == RiskLevel.MEDIUM
    # 70.1% -> HIGH
    assert analyzer.analyze(WeatherInput(rain_probability=70.1)).risk == RiskLevel.HIGH


def test_wind_thresholds(analyzer):
    """Verify wind speed thresholds (<20 km/h LOW, 20-45 km/h MEDIUM, >45 km/h HIGH)."""
    # 19.9 -> LOW
    assert analyzer.analyze(WeatherInput(wind_speed_kmh=19.9)).risk == RiskLevel.LOW
    # 20.0 -> MEDIUM
    assert analyzer.analyze(WeatherInput(wind_speed_kmh=20.0)).risk == RiskLevel.MEDIUM
    # 45.0 -> MEDIUM
    assert analyzer.analyze(WeatherInput(wind_speed_kmh=45.0)).risk == RiskLevel.MEDIUM
    # 45.1 -> HIGH
    assert analyzer.analyze(WeatherInput(wind_speed_kmh=45.1)).risk == RiskLevel.HIGH


def test_visibility_thresholds(analyzer):
    """Verify visibility thresholds (<1000m HIGH, 1000m-5000m MEDIUM, >5000m LOW)."""
    # 999.0m -> HIGH (Note: Lower visibility is higher risk)
    assert analyzer.analyze(WeatherInput(visibility_meters=999.0)).risk == RiskLevel.HIGH
    # 1000.0m -> MEDIUM
    assert analyzer.analyze(WeatherInput(visibility_meters=1000.0)).risk == RiskLevel.MEDIUM
    # 5000.0m -> MEDIUM
    assert analyzer.analyze(WeatherInput(visibility_meters=5000.0)).risk == RiskLevel.MEDIUM
    # 5001.0m -> LOW
    assert analyzer.analyze(WeatherInput(visibility_meters=5001.0)).risk == RiskLevel.LOW


def test_lightning_override(analyzer):
    """Verify that active lightning overrides other metrics to immediately force HIGH risk."""
    # Other metrics are low risk (rain 5%, wind 5, visibility 10k), but lightning is True
    inp = WeatherInput(
        rain_probability=5.0, wind_speed_kmh=5.0,
        lightning_detected=True, visibility_meters=10000.0
    )
    assert analyzer.analyze(inp).risk == RiskLevel.HIGH


def test_overall_risk_precedence(analyzer):
    """Verify overall risk assessment priority (HIGH > MEDIUM > LOW)."""
    # All LOW -> LOW
    inp_all_low = WeatherInput(
        rain_probability=10.0, wind_speed_kmh=10.0,
        lightning_detected=False, visibility_meters=10000.0
    )
    assert analyzer.analyze(inp_all_low).risk == RiskLevel.LOW

    # One MEDIUM, others LOW -> MEDIUM
    inp_one_med = WeatherInput(
        rain_probability=40.0, wind_speed_kmh=10.0,  # MEDIUM, LOW
        lightning_detected=False, visibility_meters=10000.0
    )
    assert analyzer.analyze(inp_one_med).risk == RiskLevel.MEDIUM

    # One HIGH, one MEDIUM -> HIGH (HIGH dominates)
    inp_high_dom = WeatherInput(
        rain_probability=40.0, wind_speed_kmh=50.0,  # MEDIUM, HIGH
        lightning_detected=False, visibility_meters=10000.0
    )
    assert analyzer.analyze(inp_high_dom).risk == RiskLevel.HIGH


def test_predictions(analyzer):
    """Verify operational impact forecasts, expected delays, and recommendations."""
    # Test lightning prediction
    inp_lightning = WeatherInput(lightning_detected=True)
    pred_l = analyzer.analyze(inp_lightning).prediction
    assert "Critical" in pred_l.expected_operational_impact
    assert pred_l.expected_delay_minutes == 45
    assert "Pause outdoor operations" in pred_l.recommendation

    # Test heavy rain/low visibility prediction
    inp_heavy_rain = WeatherInput(rain_probability=95.0, lightning_detected=False)
    pred_r = analyzer.analyze(inp_heavy_rain).prediction
    assert "Severe rain" in pred_r.expected_operational_impact
    assert pred_r.expected_delay_minutes == 20
    assert "Open additional covered gates" in pred_r.recommendation

    # Test high wind prediction
    inp_wind = WeatherInput(wind_speed_kmh=50.0, lightning_detected=False)
    pred_w = analyzer.analyze(inp_wind).prediction
    assert "High wind" in pred_w.expected_operational_impact
    assert pred_w.expected_delay_minutes == 10
    assert "Implement temporary banner restrictions" in pred_w.recommendation

    # Test medium indicators prediction
    inp_med = WeatherInput(rain_probability=40.0, lightning_detected=False)
    pred_m = analyzer.analyze(inp_med).prediction
    assert "Medium" in pred_m.expected_operational_impact
    assert pred_m.expected_delay_minutes == 5
    assert "advise fans to carry ponchos" in pred_m.recommendation

    # Test low/clear conditions
    inp_clear = WeatherInput(
        temperature_celsius=20.0, rain_probability=5.0,
        wind_speed_kmh=5.0, lightning_detected=False,
        visibility_meters=10000.0, match_phase=MatchPhase.T_120
    )
    pred_c = analyzer.analyze(inp_clear).prediction
    assert "Low" in pred_c.expected_operational_impact
    assert pred_c.expected_delay_minutes == 0
    assert "Proceed with normal matchday operations" in pred_c.recommendation


def test_confidence_calculation(analyzer):
    """Verify confidence updates as float values (0.0-1.0) based on completeness of provided telemetry."""
    # All 6 fields provided -> 1.0 confidence
    inp_full = WeatherInput(
        temperature_celsius=25.0, rain_probability=10.0,
        wind_speed_kmh=15.0, lightning_detected=False,
        visibility_meters=9000.0, match_phase=MatchPhase.T_120
    )
    assert analyzer.analyze(inp_full).confidence == 1.0

    # 3 fields provided -> 0.5 confidence (3 / 6 = 0.5)
    inp_partial = WeatherInput(
        temperature_celsius=25.0,
        lightning_detected=False,
        match_phase=MatchPhase.T_120
    )
    assert analyzer.analyze(inp_partial).confidence == 0.5

    # 0 fields provided -> 0.0 confidence
    assert analyzer.analyze(WeatherInput()).confidence == 0.0


# ----------------------------------------------------------------------
# Simulator Tests
# ----------------------------------------------------------------------

def test_simulator_phases():
    """Verify simulator generates correct deterministic profiles for MatchPhase values."""
    sim = WeatherSimulator()

    # T-120: Sunny, no rain, normal wind
    t120 = sim.generate(MatchPhase.T_120)
    assert t120.temperature_celsius == 25.0
    assert t120.rain_probability == 5.0
    assert t120.lightning_detected is False

    # Rain Event: Heavy rain, lightning, low visibility
    rain = sim.generate(MatchPhase.RAIN_EVENT)
    assert rain.rain_probability == 95.0
    assert rain.lightning_detected is True
    assert rain.visibility_meters == 800.0

    # Full-time: Wind, light rain
    full = sim.generate(MatchPhase.FULLTIME)
    assert full.wind_speed_kmh == 48.0
    assert full.rain_probability == 35.0

    # Safe string conversion check
    assert sim.generate("Rain Event").match_phase == MatchPhase.RAIN_EVENT

    # Invalid phase throws ValueError
    with pytest.raises(ValueError):
        sim.generate("UnknownPhase")
