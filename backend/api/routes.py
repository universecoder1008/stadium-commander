"""FastAPI Routes for Stadium Commander.

This module exposes endpoints for status querying, timeline simulation,
and situation report analysis.
"""

from typing import Optional
from fastapi import APIRouter, Request, HTTPException

from models.common import MatchPhase
from api.models import CombinedSituationReport, CommanderResponse

from simulator.stadium_simulator import StadiumSimulator
from simulator.transport_simulator import TransportSimulator
from simulator.medical_simulator import MedicalSimulator
from simulator.weather_simulator import WeatherSimulator
from simulator.volunteer_simulator import VolunteerSimulator

router = APIRouter()

# In-memory simulator timeline state
PHASES = [
    MatchPhase.T_120,
    MatchPhase.T_90,
    MatchPhase.T_60,
    MatchPhase.T_30,
    MatchPhase.KICKOFF,
    MatchPhase.HALFTIME,
    MatchPhase.RAIN_EVENT,
    MatchPhase.FULLTIME
]
current_phase_index = 0
latest_report: Optional[CombinedSituationReport] = None


@router.get("/")
def read_root():
    """Returns basic service details."""
    return {
        "service": "Stadium Commander",
        "version": "1.0",
        "status": "running"
    }


@router.get("/health")
def read_health():
    """Returns application health status."""
    return {
        "status": "healthy"
    }


@router.get("/status")
def read_status():
    """Returns current simulator phase and latest CombinedSituationReport."""
    global current_phase_index, latest_report
    active_phase = PHASES[current_phase_index]
    return {
        "current_phase": active_phase.value,
        "phase_index": current_phase_index,
        "total_phases": len(PHASES),
        "latest_report": latest_report
    }


@router.post("/simulate", response_model=CommanderResponse)
def simulate_timeline(request: Request):
    """Advances the simulator timeline by one phase, runs analysis, and reasons on result."""
    global current_phase_index, latest_report
    phase = PHASES[current_phase_index]

    # Generate simulator inputs for current phase
    try:
        stadium_input = StadiumSimulator().generate()
        stadium_input.match_phase = phase.value
        stadium_input.transport_telemetry = TransportSimulator().generate(phase)
        stadium_input.medical = MedicalSimulator().generate(phase)
        stadium_input.weather = WeatherSimulator().generate(phase)
        stadium_input.volunteer = VolunteerSimulator().generate(phase)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating simulation inputs: {str(e)}"
        )

    # Advance phase pointer (wrap around timeline)
    current_phase_index = (current_phase_index + 1) % len(PHASES)

    # Orchestrate analyzers
    try:
        orchestrator = request.app.state.orchestrator
        report = orchestrator.analyze(stadium_input)
        latest_report = report
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running stadium orchestrator: {str(e)}"
        )

    # Invoke Commander reasoning
    try:
        commander = request.app.state.commander
        decision = commander.analyze(report)
        return decision
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error invoking commander agent: {str(e)}"
        )


@router.post("/analyze", response_model=CommanderResponse)
def analyze_situation_report(report: CombinedSituationReport, request: Request):
    """Invokes the Commander Agent directly on an existing situation report."""
    try:
        commander = request.app.state.commander
        decision = commander.analyze(report)
        return decision
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error invoking commander agent: {str(e)}"
        )


def reset_timeline_for_test():
    """Utility helper to reset timeline indexing back to start (used for tests)."""
    global current_phase_index, latest_report
    current_phase_index = 0
    latest_report = None
