"""Unit tests for the Stadium Commander Orchestrator.

Purpose:
    Verify the coordination of multiple analyzers, aggregation of individual responses,
    correct mapping of overall system-wide risk status via the SystemStatus enum,
    accurate timing measurements, and completion/failure tracking metrics.

AI Usage:
    - This testing module is entirely code-defined. No generative AI or LLMs are used
      for evaluating or asserting test outcomes.
"""

import pytest
from unittest.mock import Mock

from models.common import RiskLevel, MatchPhase
from models.stadium_input import StadiumInput, GateData, TransportData, ParkingData, MetroData, BusData
from models.transport_schema import TransportInput, TransportResponse, TransportPrediction
from models.medical_schema import MedicalInput, MedicalResponse, MedicalPrediction
from models.weather_schema import WeatherInput, WeatherResponse, WeatherPrediction
from models.volunteer_schema import VolunteerInput, VolunteerResponse, VolunteerPrediction
from models.crowd_schema import CrowdResponse, Prediction
from models.situation_report import SystemStatus

from orchestrator.stadium_orchestrator import StadiumOrchestrator


@pytest.fixture
def base_stadium_input():
    """Generates a default StadiumInput containing nested sub-input schemas."""
    return StadiumInput(
        current_time="18:00",
        match_phase="T-90",
        gates=[
            GateData(gate="Gate 1", occupancy=30, queue_minutes=5, entry_rate=100)
        ],
        transport=TransportData(
            parking=ParkingData(occupancy=50, available_spots=200),
            metro=MetroData(next_arrival_minutes=5, expected_passengers=1000),
            bus=BusData(delay_minutes=2)
        ),
        transport_telemetry=TransportInput(
            parking_capacity=250, parking_occupied=50,
            metro_expected=1000, metro_arrived=50, metro_delay_minutes=5,
            buses_expected=20, buses_arrived=2, bus_delay_minutes=2,
            match_phase=MatchPhase.T_90
        ),
        medical=MedicalInput(
            active_incidents=1, critical_incidents=0,
            ambulances_available=5, ambulances_total=5,
            first_aid_queue=0, medical_staff_available=10, medical_staff_total=10,
            average_response_time_minutes=2.0, match_phase=MatchPhase.T_90
        ),
        weather=WeatherInput(
            temperature_celsius=22.0, rain_probability=10.0,
            wind_speed_kmh=15.0, lightning_detected=False,
            visibility_meters=9000.0, match_phase=MatchPhase.T_90
        ),
        volunteer=VolunteerInput(
            available_volunteers=80, total_volunteers=100,
            zone_assignments={"Zone A": 20}, zone_coverage_percent=90.0,
            average_response_time_minutes=3.0, active_requests=2,
            match_phase=MatchPhase.T_90
        )
    )


def test_orchestrator_successful_execution(base_stadium_input):
    """Verify that all analyzers execute, returning correct responses, timing, and lists."""
    mock_crowd = Mock()
    mock_crowd.analyze.return_value = CrowdResponse(
        risk="LOW", confidence=100,
        predictions=[Prediction(gate="Gate 1", issue="None", eta_minutes=0)],
        reasoning=[]
    )

    mock_transport = Mock()
    mock_transport.analyze.return_value = TransportResponse(
        risk=RiskLevel.LOW, confidence=1.0, parking_occupancy_percent=20.0,
        metro_status=RiskLevel.LOW, bus_status=RiskLevel.LOW,
        arrival_prediction=TransportPrediction(remaining_spectators=0, estimated_arrival_minutes=0),
        reasoning=[]
    )

    mock_medical = Mock()
    mock_medical.analyze.return_value = MedicalResponse(
        risk=RiskLevel.LOW, confidence=1.0, ambulance_utilization_percent=0.0,
        medical_staff_utilization_percent=0.0,
        prediction=MedicalPrediction(predicted_incidents=0, resource_shortage=False, estimated_response_time=2.0),
        reasoning=[]
    )

    mock_weather = Mock()
    mock_weather.analyze.return_value = WeatherResponse(
        risk=RiskLevel.LOW, confidence=1.0, weather_status=RiskLevel.LOW,
        prediction=WeatherPrediction(expected_operational_impact="None", expected_delay_minutes=0, recommendation="None"),
        reasoning=[]
    )

    mock_volunteer = Mock()
    mock_volunteer.analyze.return_value = VolunteerResponse(
        risk=RiskLevel.LOW, confidence=1.0, volunteer_utilization_percent=20.0, coverage_percent=90.0,
        prediction=VolunteerPrediction(expected_shortage=0, recommended_redeployment="None", predicted_response_time=3.0),
        reasoning=[]
    )

    orchestrator = StadiumOrchestrator(
        crowd_analyzer=mock_crowd,
        transport_analyzer=mock_transport,
        medical_analyzer=mock_medical,
        weather_analyzer=mock_weather,
        volunteer_analyzer=mock_volunteer
    )

    report = orchestrator.analyze(base_stadium_input)

    # Assertions
    assert report.timestamp == "18:00"
    assert report.match_phase == "T-90"
    assert report.system_status == SystemStatus.NORMAL
    assert report.crowd.risk == "LOW"
    assert report.transport.risk == RiskLevel.LOW
    assert report.medical.risk == RiskLevel.LOW
    assert report.weather.risk == RiskLevel.LOW
    assert report.volunteer.risk == RiskLevel.LOW

    # Timing assertions
    assert isinstance(report.processing_time_ms, float)
    assert report.processing_time_ms >= 0.0

    # completed/failed lists verification
    assert sorted(report.analyzers_completed) == ["crowd", "medical", "transport", "volunteer", "weather"]
    assert report.analyzers_failed == {}

    # Verify calls
    mock_crowd.analyze.assert_called_once_with(base_stadium_input)
    mock_transport.analyze.assert_called_once()
    mock_medical.analyze.assert_called_once_with(base_stadium_input.medical)
    mock_weather.analyze.assert_called_once_with(base_stadium_input.weather)
    mock_volunteer.analyze.assert_called_once_with(base_stadium_input.volunteer)


def test_system_status_calculations(base_stadium_input):
    """Verify system status maps to WARNING (if any is MEDIUM) or CRITICAL (if any is HIGH/CRITICAL)."""
    # 1. Test WARNING trigger (Medical is MEDIUM, others are LOW)
    mock_crowd = Mock()
    mock_crowd.analyze.return_value = CrowdResponse(risk="LOW", confidence=100, predictions=[], reasoning=[])
    mock_transport = Mock()
    mock_transport.analyze.return_value = TransportResponse(
        risk=RiskLevel.LOW, confidence=1.0, parking_occupancy_percent=0.0, metro_status=RiskLevel.LOW, bus_status=RiskLevel.LOW,
        arrival_prediction=TransportPrediction(remaining_spectators=0, estimated_arrival_minutes=0), reasoning=[]
    )
    mock_medical = Mock()
    mock_medical.analyze.return_value = MedicalResponse(
        risk=RiskLevel.MEDIUM, confidence=1.0, ambulance_utilization_percent=0.0, medical_staff_utilization_percent=0.0,
        prediction=MedicalPrediction(predicted_incidents=0, resource_shortage=False, estimated_response_time=2.0), reasoning=[]
    )
    mock_weather = Mock()
    mock_weather.analyze.return_value = WeatherResponse(
        risk=RiskLevel.LOW, confidence=1.0, weather_status=RiskLevel.LOW,
        prediction=WeatherPrediction(expected_operational_impact="None", expected_delay_minutes=0, recommendation="None"), reasoning=[]
    )
    mock_volunteer = Mock()
    mock_volunteer.analyze.return_value = VolunteerResponse(
        risk=RiskLevel.LOW, confidence=1.0, volunteer_utilization_percent=0.0, coverage_percent=100.0,
        prediction=VolunteerPrediction(expected_shortage=0, recommended_redeployment="None", predicted_response_time=3.0), reasoning=[]
    )

    orchestrator = StadiumOrchestrator(
        crowd_analyzer=mock_crowd, transport_analyzer=mock_transport,
        medical_analyzer=mock_medical, weather_analyzer=mock_weather,
        volunteer_analyzer=mock_volunteer
    )

    report = orchestrator.analyze(base_stadium_input)
    assert report.system_status == SystemStatus.WARNING

    # 2. Test CRITICAL trigger (Weather is HIGH, others are LOW)
    mock_weather.analyze.return_value = WeatherResponse(
        risk=RiskLevel.HIGH, confidence=1.0, weather_status=RiskLevel.HIGH,
        prediction=WeatherPrediction(expected_operational_impact="None", expected_delay_minutes=0, recommendation="None"), reasoning=[]
    )
    report2 = orchestrator.analyze(base_stadium_input)
    assert report2.system_status == SystemStatus.CRITICAL

    # 3. Test CRITICAL trigger from Crowd (Crowd is CRITICAL)
    mock_weather.analyze.return_value = WeatherResponse(
        risk=RiskLevel.LOW, confidence=1.0, weather_status=RiskLevel.LOW,
        prediction=WeatherPrediction(expected_operational_impact="None", expected_delay_minutes=0, recommendation="None"), reasoning=[]
    )
    mock_crowd.analyze.return_value = CrowdResponse(risk="CRITICAL", confidence=100, predictions=[], reasoning=[])
    report3 = orchestrator.analyze(base_stadium_input)
    assert report3.system_status == SystemStatus.CRITICAL


def test_graceful_exception_handling(base_stadium_input):
    """Verify that when multiple analyzers throw errors, remaining analyzers run and errors are recorded."""
    mock_crowd = Mock()
    mock_crowd.analyze.side_effect = RuntimeError("Crowd analysis crashed")

    mock_transport = Mock()
    mock_transport.analyze.side_effect = ValueError("Transport telemetry parse failure")

    mock_medical = Mock()
    mock_medical.analyze.return_value = MedicalResponse(
        risk=RiskLevel.MEDIUM, confidence=1.0, ambulance_utilization_percent=0.0, medical_staff_utilization_percent=0.0,
        prediction=MedicalPrediction(predicted_incidents=0, resource_shortage=False, estimated_response_time=2.0), reasoning=[]
    )

    mock_weather = Mock()
    mock_weather.analyze.return_value = WeatherResponse(
        risk=RiskLevel.LOW, confidence=1.0, weather_status=RiskLevel.LOW,
        prediction=WeatherPrediction(expected_operational_impact="None", expected_delay_minutes=0, recommendation="None"), reasoning=[]
    )

    mock_volunteer = Mock()
    mock_volunteer.analyze.return_value = VolunteerResponse(
        risk=RiskLevel.LOW, confidence=1.0, volunteer_utilization_percent=0.0, coverage_percent=100.0,
        prediction=VolunteerPrediction(expected_shortage=0, recommended_redeployment="None", predicted_response_time=3.0), reasoning=[]
    )

    orchestrator = StadiumOrchestrator(
        crowd_analyzer=mock_crowd, transport_analyzer=mock_transport,
        medical_analyzer=mock_medical, weather_analyzer=mock_weather,
        volunteer_analyzer=mock_volunteer
    )

    report = orchestrator.analyze(base_stadium_input)

    # Check report content and status
    assert report.crowd is None
    assert report.transport is None
    assert report.medical.risk == RiskLevel.MEDIUM
    assert report.system_status == SystemStatus.WARNING  # Derived from successful analyzer (medical = MEDIUM)

    # Completion lists and timing assertions
    assert sorted(report.analyzers_completed) == ["medical", "volunteer", "weather"]
    assert "crowd" in report.analyzers_failed
    assert "transport" in report.analyzers_failed
    assert report.analyzers_failed["crowd"] == "Crowd analysis crashed"
    assert report.analyzers_failed["transport"] == "Transport telemetry parse failure"
    assert report.processing_time_ms >= 0.0

    # Verify execution of others
    mock_medical.analyze.assert_called_once()
    mock_weather.analyze.assert_called_once()
    mock_volunteer.analyze.assert_called_once()
