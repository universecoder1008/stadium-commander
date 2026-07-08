"""API Route tests for the Stadium Commander FastAPI app.

Purpose:
    Verify the endpoints (ROOT, health, status, simulation, analysis) using TestClient,
    assert HTTP status codes (200, 400, 500), and test payload validations.

AI Usage:
    - This testing module is entirely code-defined. No generative AI or LLMs are used
      for evaluating or asserting test outcomes.
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from main import app
from api.models import CommanderResponse
from api.routes import reset_timeline_for_test


@pytest.fixture
def test_client():
    """Configures TestClient and mocks the Commander Agent dependency to prevent GenAI network calls."""
    mock_commander = Mock()
    mock_commander.analyze.return_value = CommanderResponse(
        priority="CRITICAL",
        top_risk="Lightning warning active",
        summary="Lightning hazard detected in stadium vicinity.",
        actions=["Pause match", "Evacuate stands"],
        estimated_impact="Reduces public exposure to lightning hazard.",
        confidence=0.98
    )
    # Inject mock commander agent into FastAPI app state
    app.state.commander = mock_commander

    # Reset simulation pointer
    reset_timeline_for_test()

    return TestClient(app)


def test_get_root(test_client):
    """Verify GET / returns correct service name and version metadata."""
    response = test_client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["service"] == "Stadium Commander"
    assert json_data["status"] == "running"
    assert json_data["version"] == "1.0"


def test_get_health(test_client):
    """Verify GET /health returns successful status."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_status(test_client):
    """Verify GET /status returns the current active match phase and latest situation report."""
    response = test_client.get("/status")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["current_phase"] == "T-120"
    assert json_data["phase_index"] == 0
    assert json_data["latest_report"] is None


def test_post_simulate(test_client):
    """Verify POST /simulate advances simulation phase, updates latest_report, and returns a CommanderResponse."""
    # First simulation call advances T-120
    response = test_client.post("/simulate")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["priority"] == "CRITICAL"
    assert json_data["confidence"] == 0.98
    assert "Pause match" in json_data["actions"]

    # Verify timeline index advanced to phase 1 (T-90)
    status_response = test_client.get("/status")
    status_data = status_response.json()
    assert status_data["phase_index"] == 1
    assert status_data["latest_report"] is not None
    assert status_data["latest_report"]["match_phase"] == "T-120"


def test_post_analyze(test_client):
    """Verify POST /analyze receives situation report and invokes the commander correctly."""
    valid_report = {
        "timestamp": "19:30",
        "match_phase": "Rain Event",
        "system_status": "CRITICAL",
        "analyzers_completed": ["weather", "volunteer"],
        "analyzers_failed": {},
        "processing_time_ms": 15.5
    }

    response = test_client.post("/analyze", json=valid_report)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["priority"] == "CRITICAL"
    assert json_data["top_risk"] == "Lightning warning active"


def test_invalid_payload_error_handling(test_client):
    """Verify that invalid Pydantic input models result in a customized HTTP 400 bad request."""
    # Missing required 'timestamp' field
    invalid_report = {
        "match_phase": "Halftime",
        "system_status": "NORMAL",
        "analyzers_completed": [],
        "analyzers_failed": {},
        "processing_time_ms": 5.0
    }

    response = test_client.post("/analyze", json=invalid_report)
    # The custom validation handler intercepts and returns 400 without exposing stack traces
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid input"}


def test_simulate_entire_timeline_loop(test_client):
    """Verify that repeatedly calling POST /simulate runs through all 8 phases sequence and wraps back cleanly without 500 errors."""
    expected_phases = [
        "T-120", "T-90", "T-60", "T-30", "Kickoff", "Halftime", "Rain Event", "Full-time"
    ]
    
    # Run loop through all phases twice to verify safe wrap-arounds
    for _ in range(2):
        for expected_phase in expected_phases:
            # Check current phase before simulating
            status_resp = test_client.get("/status")
            assert status_resp.status_code == 200
            assert status_resp.json()["current_phase"] == expected_phase
            
            # Post simulate to advance
            response = test_client.post("/simulate")
            assert response.status_code == 200
            assert response.json()["priority"] == "CRITICAL"
