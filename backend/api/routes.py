"""FastAPI Routes for Stadium Commander.

This module exposes endpoints for status querying, timeline simulation,
and situation report analysis.
"""

from typing import Optional
import logging
import traceback
from fastapi import APIRouter, Request, HTTPException

logger = logging.getLogger("stadium_commander.api")

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
    
    # Verify state dependencies are initialized
    if not hasattr(request.app.state, "orchestrator") or not request.app.state.orchestrator:
        logger.error("StadiumOrchestrator dependency is not initialized in app state.")
        raise HTTPException(status_code=500, detail="Stadium orchestrator is offline")
    
    if not hasattr(request.app.state, "commander") or not request.app.state.commander:
        logger.error("CommanderAgent dependency is not initialized in app state.")
        raise HTTPException(status_code=500, detail="Commander agent is offline")
    
    # Defensive index boundary check
    if not (0 <= current_phase_index < len(PHASES)):
        logger.warning("Timeline index %d out of bounds. Resetting to 0.", current_phase_index)
        current_phase_index = 0
        
    phase = PHASES[current_phase_index]
    next_phase_index = (current_phase_index + 1) % len(PHASES)
    next_phase = PHASES[next_phase_index]

    # Generate simulator inputs for current phase
    affected_simulator = "None"
    try:
        affected_simulator = "StadiumSimulator"
        stadium_input = StadiumSimulator().generate()
        stadium_input.match_phase = phase.value
        
        affected_simulator = "TransportSimulator"
        stadium_input.transport_telemetry = TransportSimulator().generate(phase)
        
        affected_simulator = "MedicalSimulator"
        stadium_input.medical = MedicalSimulator().generate(phase)
        
        affected_simulator = "WeatherSimulator"
        stadium_input.weather = WeatherSimulator().generate(phase)
        
        affected_simulator = "VolunteerSimulator"
        stadium_input.volunteer = VolunteerSimulator().generate(phase)
    except Exception as exc:
        tb_str = traceback.format_exc()
        logger.error(
            "POST /simulate failed during telemetry generation.\n"
            "Current Phase: %s, Next Phase: %s, Timeline Index: %d\n"
            "Affected Simulator: %s, Exception Type: %s\n"
            "Traceback:\n%s",
            phase.value, next_phase.value, current_phase_index,
            affected_simulator, type(exc).__name__, tb_str
        )
        raise HTTPException(
            status_code=500,
            detail=f"Telemetry generation error on simulator '{affected_simulator}': {str(exc)}"
        )

    # Advance phase pointer (wrap around timeline)
    current_phase_index = next_phase_index

    # Orchestrate analyzers
    try:
        orchestrator = request.app.state.orchestrator
        report = orchestrator.analyze(stadium_input)
        latest_report = report
    except Exception as exc:
        tb_str = traceback.format_exc()
        logger.error(
            "POST /simulate failed during analysis orchestration.\n"
            "Current Phase: %s, Next Phase: %s, Timeline Index: %d\n"
            "Exception Type: %s\n"
            "Traceback:\n%s",
            phase.value, next_phase.value, current_phase_index,
            type(exc).__name__, tb_str
        )
        raise HTTPException(
            status_code=500,
            detail=f"Stadium orchestrator analysis failed: {str(exc)}"
        )

    # Invoke Commander reasoning
    try:
        commander = request.app.state.commander
        decision = commander.analyze(report)
        return decision
    except Exception as exc:
        tb_str = traceback.format_exc()
        logger.error(
            "POST /simulate failed during commander reasoning agent.\n"
            "Current Phase: %s, Next Phase: %s, Timeline Index: %d\n"
            "Exception Type: %s\n"
            "Traceback:\n%s",
            phase.value, next_phase.value, current_phase_index,
            type(exc).__name__, tb_str
        )
        raise HTTPException(
            status_code=500,
            detail=f"Commander agent reasoning failed: {str(exc)}"
        )


@router.post("/analyze", response_model=CommanderResponse)
def analyze_situation_report(report: CombinedSituationReport, request: Request):
    """Invokes the Commander Agent directly on an existing situation report."""
    if not hasattr(request.app.state, "commander") or not request.app.state.commander:
        logger.error("CommanderAgent dependency is not initialized in app state.")
        raise HTTPException(status_code=500, detail="Commander agent is offline")
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
