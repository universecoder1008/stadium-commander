"""Unit tests for the Stadium Commander Commander Agent.

Purpose:
    Verify prompt loading, JSON parsing, validation errors, and retry behaviors
    of the CommanderAgent.

AI Usage:
    - This testing module is entirely code-defined. No generative AI or LLMs are used
      for evaluating or asserting test outcomes.
"""

import pytest
from unittest.mock import Mock

from models.situation_report import CombinedSituationReport, SystemStatus
from models.commander_schema import CommanderResponse
from agents.commander_agent import CommanderAgent


@pytest.fixture
def dummy_report():
    """Generates an empty dummy CombinedSituationReport for testing."""
    return CombinedSituationReport(
        timestamp="12:00",
        match_phase="T-120",
        system_status=SystemStatus.NORMAL,
        analyzers_completed=[],
        analyzers_failed={},
        processing_time_ms=10.0
    )


def test_commander_agent_successful_run(dummy_report):
    """Verify that a standard JSON response from Gemini is correctly parsed and validated."""
    mock_response = Mock()
    mock_response.text = """
    {
      "priority": "HIGH",
      "top_risk": "Extreme weather incoming",
      "summary": "Severe thunderstorm warning during halftime.",
      "actions": [
        "Move fans to covered concourses",
        "Advise volunteers to move indoors"
      ],
      "estimated_impact": "Reduces spectator hazard from lightning strikes.",
      "confidence": 0.95
    }
    """
    mock_client = Mock()
    mock_client.models.generate_content.return_value = mock_response

    system_prompt = "You are Stadium Commander."
    agent = CommanderAgent(client=mock_client, system_prompt=system_prompt)
    result = agent.analyze(dummy_report)

    # Assertions
    assert result.priority == "HIGH"
    assert result.top_risk == "Extreme weather incoming"
    assert result.confidence == 0.95
    assert len(result.actions) == 2
    mock_client.models.generate_content.assert_called_once()


def test_commander_agent_retry_on_first_failure(dummy_report):
    """Verify that if JSON parsing fails on the first attempt, the agent retries once."""
    mock_response_fail = Mock()
    mock_response_fail.text = "This is not JSON content at all"

    mock_response_success = Mock()
    mock_response_success.text = """
    {
      "priority": "CRITICAL",
      "top_risk": "First aid queue congestion",
      "summary": "First aid queues are overwhelmed.",
      "actions": ["Deploy backup paramedics"],
      "estimated_impact": "Reduces dispatch times.",
      "confidence": 1.0
    }
    """

    mock_client = Mock()
    mock_client.models.generate_content.side_effect = [
        mock_response_fail,
        mock_response_success
    ]

    agent = CommanderAgent(client=mock_client, system_prompt="System Prompt")
    result = agent.analyze(dummy_report)

    assert result.priority == "CRITICAL"
    assert result.confidence == 1.0
    # Assert generate_content was called twice due to the single retry mechanism
    assert mock_client.models.generate_content.call_count == 2


def test_commander_agent_failure_after_two_attempts(dummy_report):
    """Verify that if parsing fails on both attempts, the agent returns the fallback response."""
    mock_response_fail1 = Mock()
    mock_response_fail1.text = "First failure text"
    mock_response_fail2 = Mock()
    mock_response_fail2.text = "Second failure text"

    mock_client = Mock()
    mock_client.models.generate_content.side_effect = [
        mock_response_fail1,
        mock_response_fail2
    ]

    agent = CommanderAgent(client=mock_client, system_prompt="System Prompt")
    result = agent.analyze(dummy_report)

    assert result.priority == "WARNING"
    assert result.top_risk == "AI reasoning temporarily unavailable"
    assert result.confidence == 0.75
    assert mock_client.models.generate_content.call_count == 2


def test_commander_agent_markdown_stripping(dummy_report):
    """Verify that markdown JSON wrapper blocks (e.g. ```json ... ```) are correctly stripped and parsed."""
    mock_response = Mock()
    mock_response.text = """```json
    {
      "priority": "LOW",
      "top_risk": "None",
      "summary": "Normal operation.",
      "actions": ["Maintain baseline patrol"],
      "estimated_impact": "Maintains stability.",
      "confidence": 0.8
    }
    ```"""
    mock_client = Mock()
    mock_client.models.generate_content.return_value = mock_response

    agent = CommanderAgent(client=mock_client, system_prompt="System Prompt")
    result = agent.analyze(dummy_report)

    assert result.priority == "LOW"
    assert result.confidence == 0.8
