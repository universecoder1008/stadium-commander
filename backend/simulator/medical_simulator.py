"""Medical Simulator for Stadium Commander.

This module provides deterministic simulation scenarios matching the football match timeline.

Purpose:
    Generate realistic, reproducible medical telemetry data for the Stadium Commander platform,
    allowing operators and testers to validate medical risk assessments under specific phases.

Inputs:
    - MatchPhase enum value (e.g., MatchPhase.T_30, MatchPhase.RAIN_EVENT).

Outputs:
    - MedicalInput: Validated Pydantic model populated with deterministic telemetry data
      matching the selected timeline phase.

Deterministic Guarantees:
    - Generating data for the same MatchPhase will always return identical telemetry.
    - No random variation is introduced; incident counts, queues, and resources
      are statically mapped per phase.

AI Usage:
    - This module relies entirely on hardcoded dictionary profiles. No AI models or random
      generators are utilized in creating the simulation telemetry.
"""

from models.transport_schema import MatchPhase
from models.medical_schema import MedicalInput


class MedicalSimulator:
    """Simulator for generating deterministic MedicalInput telemetry based on match phases."""

    # Predefined simulation profiles for each MatchPhase timeline point
    SIMULATION_PROFILES = {
        MatchPhase.T_120: {
            "active_incidents": 1,
            "critical_incidents": 0,
            "ambulances_available": 10,
            "ambulances_total": 10,
            "first_aid_queue": 0,
            "medical_staff_available": 50,
            "medical_staff_total": 50,
            "average_response_time_minutes": 2,
            "match_phase": MatchPhase.T_120,
        },
        MatchPhase.T_90: {
            "active_incidents": 3,
            "critical_incidents": 0,
            "ambulances_available": 9,
            "ambulances_total": 10,
            "first_aid_queue": 2,
            "medical_staff_available": 48,
            "medical_staff_total": 50,
            "average_response_time_minutes": 3,
            "match_phase": MatchPhase.T_90,
        },
        MatchPhase.T_60: {
            "active_incidents": 6,
            "critical_incidents": 1,
            "ambulances_available": 8,
            "ambulances_total": 10,
            "first_aid_queue": 6,
            "medical_staff_available": 42,
            "medical_staff_total": 50,
            "average_response_time_minutes": 4,
            "match_phase": MatchPhase.T_60,
        },
        MatchPhase.T_30: {
            "active_incidents": 12,
            "critical_incidents": 2,
            "ambulances_available": 5,
            "ambulances_total": 10,
            "first_aid_queue": 12,
            "medical_staff_available": 30,
            "medical_staff_total": 50,
            "average_response_time_minutes": 7,
            "match_phase": MatchPhase.T_30,
        },
        MatchPhase.KICKOFF: {
            "active_incidents": 8,
            "critical_incidents": 0,
            "ambulances_available": 7,
            "ambulances_total": 10,
            "first_aid_queue": 4,
            "medical_staff_available": 40,
            "medical_staff_total": 50,
            "average_response_time_minutes": 4,
            "match_phase": MatchPhase.KICKOFF,
        },
        MatchPhase.HALFTIME: {
            "active_incidents": 10,
            "critical_incidents": 1,
            "ambulances_available": 6,
            "ambulances_total": 10,
            "first_aid_queue": 8,
            "medical_staff_available": 35,
            "medical_staff_total": 50,
            "average_response_time_minutes": 5,
            "match_phase": MatchPhase.HALFTIME,
        },
        MatchPhase.RAIN_EVENT: {
            "active_incidents": 18,
            "critical_incidents": 3,
            "ambulances_available": 3,
            "ambulances_total": 10,
            "first_aid_queue": 22,
            "medical_staff_available": 20,
            "medical_staff_total": 50,
            "average_response_time_minutes": 12,
            "match_phase": MatchPhase.RAIN_EVENT,
        },
        MatchPhase.FULLTIME: {
            "active_incidents": 25,
            "critical_incidents": 4,
            "ambulances_available": 1,
            "ambulances_total": 10,
            "first_aid_queue": 30,
            "medical_staff_available": 10,
            "medical_staff_total": 50,
            "average_response_time_minutes": 16,
            "match_phase": MatchPhase.FULLTIME,
        },
    }

    def generate(self, match_phase: MatchPhase) -> MedicalInput:
        """Generates deterministic MedicalInput for the specified match phase.

        Args:
            match_phase: The MatchPhase enum value (e.g., MatchPhase.T_120).

        Returns:
            A MedicalInput object populated with deterministic telemetry.

        Raises:
            ValueError: If the match phase is unknown.
        """
        # Safe conversion if passed as a string representation
        if isinstance(match_phase, str):
            try:
                match_phase = MatchPhase(match_phase)
            except ValueError:
                pass

        if match_phase not in self.SIMULATION_PROFILES:
            supported_phases = ", ".join(m.value for m in MatchPhase)
            raise ValueError(
                f"Unknown match phase '{match_phase}'. Supported phases are: {supported_phases}"
            )

        profile = self.SIMULATION_PROFILES[match_phase]
        return MedicalInput(**profile)
