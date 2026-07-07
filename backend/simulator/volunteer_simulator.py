"""Volunteer Simulator for Stadium Commander.

This module provides deterministic simulation scenarios matching the football match timeline.

Purpose:
    Generate realistic, reproducible volunteer telemetry data for the Stadium Commander platform,
    allowing operators and testers to validate volunteer risk assessments under specific phases.

Inputs:
    - MatchPhase enum value (e.g., MatchPhase.T_30, MatchPhase.RAIN_EVENT).

Outputs:
    - VolunteerInput: Validated Pydantic model populated with deterministic telemetry data
      matching the selected timeline phase.

Deterministic Guarantees:
    - Generating data for the same MatchPhase will always return identical telemetry.
    - No random variation is introduced; volunteer counts, queues, and response times
      are statically mapped per phase.

AI Usage:
    - This module relies entirely on hardcoded dictionary profiles. No AI models or random
      generators are utilized in creating the simulation telemetry.
"""

from models.common import MatchPhase
from models.volunteer_schema import VolunteerInput


class VolunteerSimulator:
    """Simulator for generating deterministic VolunteerInput telemetry based on match phases."""

    # Predefined simulation profiles for each MatchPhase timeline point
    SIMULATION_PROFILES = {
        MatchPhase.T_120: {
            "available_volunteers": 90,
            "total_volunteers": 100,
            "zone_assignments": {"Zone A": 20, "Zone B": 30, "Zone C": 40},
            "zone_coverage_percent": 95.0,
            "average_response_time_minutes": 2.0,
            "active_requests": 2,
            "match_phase": MatchPhase.T_120,
        },
        MatchPhase.T_90: {
            "available_volunteers": 75,
            "total_volunteers": 100,
            "zone_assignments": {"Zone A": 35, "Zone B": 30, "Zone C": 10},
            "zone_coverage_percent": 90.0,
            "average_response_time_minutes": 3.0,
            "active_requests": 5,
            "match_phase": MatchPhase.T_90,
        },
        MatchPhase.T_60: {
            "available_volunteers": 50,
            "total_volunteers": 100,
            "zone_assignments": {"Zone A": 40, "Zone B": 30, "Zone C": 10},
            "zone_coverage_percent": 78.0,
            "average_response_time_minutes": 4.0,
            "active_requests": 8,
            "match_phase": MatchPhase.T_60,
        },
        MatchPhase.T_30: {
            "available_volunteers": 15,
            "total_volunteers": 100,
            "zone_assignments": {"Zone A": 50, "Zone B": 30, "Zone C": 5},
            "zone_coverage_percent": 70.0,
            "average_response_time_minutes": 8.0,
            "active_requests": 18,
            "match_phase": MatchPhase.T_30,
        },
        MatchPhase.KICKOFF: {
            "available_volunteers": 25,
            "total_volunteers": 100,
            "zone_assignments": {"Zone A": 45, "Zone B": 25, "Zone C": 5},
            "zone_coverage_percent": 85.0,
            "average_response_time_minutes": 4.0,
            "active_requests": 6,
            "match_phase": MatchPhase.KICKOFF,
        },
        MatchPhase.HALFTIME: {
            "available_volunteers": 30,
            "total_volunteers": 100,
            "zone_assignments": {"Zone A": 20, "Zone B": 45, "Zone C": 5},
            "zone_coverage_percent": 82.0,
            "average_response_time_minutes": 4.5,
            "active_requests": 12,
            "match_phase": MatchPhase.HALFTIME,
        },
        MatchPhase.RAIN_EVENT: {
            "available_volunteers": 10,
            "total_volunteers": 100,
            "zone_assignments": {"Zone A": 40, "Zone B": 30, "Zone C": 20},
            "zone_coverage_percent": 45.0,
            "average_response_time_minutes": 16.0,
            "active_requests": 35,
            "match_phase": MatchPhase.RAIN_EVENT,
        },
        MatchPhase.FULLTIME: {
            "available_volunteers": 5,
            "total_volunteers": 100,
            "zone_assignments": {"Zone A": 60, "Zone B": 25, "Zone C": 10},
            "zone_coverage_percent": 65.0,
            "average_response_time_minutes": 18.0,
            "active_requests": 40,
            "match_phase": MatchPhase.FULLTIME,
        },
    }

    def generate(self, match_phase: MatchPhase) -> VolunteerInput:
        """Generates deterministic VolunteerInput for the specified match phase.

        Args:
            match_phase: The MatchPhase enum value (e.g., MatchPhase.T_120).

        Returns:
            A VolunteerInput object populated with deterministic telemetry.

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
        return VolunteerInput(**profile)
