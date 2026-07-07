"""Transport Simulator for Stadium Commander.

This module provides deterministic simulation scenarios matching the football match timeline.

Purpose:
    Generate realistic, reproducible telemetry data for the Stadium Commander platform,
    allowing operators and testers to validate transport risk assessments under specific phases.

Inputs:
    - MatchPhase enum value (e.g., MatchPhase.T_30, MatchPhase.FULLTIME).

Outputs:
    - TransportInput: Validated Pydantic model populated with deterministic telemetry data
      matching the selected timeline phase.

Deterministic Guarantees:
    - Generating data for the same MatchPhase will always return identical telemetry.
    - No random variation is introduced; parking occupancy, passenger volumes, and delay
      times are statically mapped per phase.

AI Usage:
    - This module relies entirely on hardcoded dictionary profiles. No AI models or random
      generators are utilized in creating the simulation telemetry.
"""

from models.common import MatchPhase
from models.transport_schema import TransportInput



class TransportSimulator:
    """Simulator for generating deterministic TransportInput telemetry based on match phases."""

    # Predefined simulation profiles for each MatchPhase timeline point
    SIMULATION_PROFILES = {
        MatchPhase.T_120: {
            "parking_capacity": 1000,
            "parking_occupied": 100,  # 10%
            "metro_expected": 10000,
            "metro_arrived": 1000,
            "metro_delay_minutes": 0,  # Normal Metro
            "buses_expected": 4000,
            "buses_arrived": 400,
            "bus_delay_minutes": 0,  # Normal Bus
            "match_phase": MatchPhase.T_120,
        },
        MatchPhase.T_90: {
            "parking_capacity": 1000,
            "parking_occupied": 400,  # 40%
            "metro_expected": 10000,
            "metro_arrived": 3000,  # Metro arriving
            "metro_delay_minutes": 2,
            "buses_expected": 4000,
            "buses_arrived": 1200,
            "bus_delay_minutes": 1,
            "match_phase": MatchPhase.T_90,
        },
        MatchPhase.T_60: {
            "parking_capacity": 1000,
            "parking_occupied": 700,  # 70%
            "metro_expected": 10000,
            "metro_arrived": 6500,  # Metro surge
            "metro_delay_minutes": 8,  # Medium delay
            "buses_expected": 4000,
            "buses_arrived": 2400,
            "bus_delay_minutes": 4,
            "match_phase": MatchPhase.T_60,
        },
        MatchPhase.T_30: {
            "parking_capacity": 1000,
            "parking_occupied": 900,  # 90%
            "metro_expected": 10000,
            "metro_arrived": 8000,
            "metro_delay_minutes": 20,  # Metro delay (HIGH)
            "buses_expected": 4000,
            "buses_arrived": 3200,
            "bus_delay_minutes": 18,  # Bus delay (HIGH)
            "match_phase": MatchPhase.T_30,
        },
        MatchPhase.KICKOFF: {
            "parking_capacity": 1000,
            "parking_occupied": 1000,  # Parking full (100% - HIGH)
            "metro_expected": 10000,
            "metro_arrived": 9800,  # Transport stabilizes
            "metro_delay_minutes": 3,
            "buses_expected": 4000,
            "buses_arrived": 3900,  # Transport stabilizes
            "bus_delay_minutes": 2,
            "match_phase": MatchPhase.KICKOFF,
        },
        MatchPhase.HALFTIME: {
            "parking_capacity": 1000,
            "parking_occupied": 1000,
            "metro_expected": 100,  # Minimal transport activity
            "metro_arrived": 90,
            "metro_delay_minutes": 0,
            "buses_expected": 50,
            "buses_arrived": 45,
            "bus_delay_minutes": 0,
            "match_phase": MatchPhase.HALFTIME,
        },
        MatchPhase.FULLTIME: {
            "parking_capacity": 1000,
            "parking_occupied": 800,
            "metro_expected": 12000,  # Heavy metro demand (Exit rush)
            "metro_arrived": 2000,
            "metro_delay_minutes": 25,  # HIGH delay
            "buses_expected": 5000,  # Heavy bus demand (Exit rush)
            "buses_arrived": 800,
            "bus_delay_minutes": 30,  # HIGH delay
            "match_phase": MatchPhase.FULLTIME,
        },
    }

    def generate(self, match_phase: MatchPhase) -> TransportInput:
        """Generates deterministic TransportInput for the specified match phase.

        Args:
            match_phase: The MatchPhase enum value (e.g., MatchPhase.T_120).

        Returns:
            A TransportInput object populated with deterministic telemetry.

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
        return TransportInput(**profile)
