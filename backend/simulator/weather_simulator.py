"""Weather Simulator for Stadium Commander.

This module provides deterministic simulation scenarios matching the football match timeline.

Purpose:
    Generate realistic, reproducible weather telemetry data for the Stadium Commander platform,
    allowing operators and testers to validate weather risk assessments under specific phases.

Inputs:
    - MatchPhase enum value (e.g., MatchPhase.T_30, MatchPhase.RAIN_EVENT).

Outputs:
    - WeatherInput: Validated Pydantic model populated with deterministic telemetry data
      matching the selected timeline phase.

Deterministic Guarantees:
    - Generating data for the same MatchPhase will always return identical telemetry.
    - No random variation is introduced; temperature, rain, wind, lightning, and visibility
      are statically mapped per phase.

AI Usage:
    - This module relies entirely on hardcoded dictionary profiles. No AI models or random
      generators are utilized in creating the simulation telemetry.
"""

from models.common import MatchPhase
from models.weather_schema import WeatherInput



class WeatherSimulator:
    """Simulator for generating deterministic WeatherInput telemetry based on match phases."""

    # Predefined simulation profiles for each MatchPhase timeline point
    SIMULATION_PROFILES = {
        MatchPhase.T_120: {
            "temperature_celsius": 25.0,
            "rain_probability": 5.0,
            "wind_speed_kmh": 10.0,
            "lightning_detected": False,
            "visibility_meters": 10000.0,
            "match_phase": MatchPhase.T_120,
        },
        MatchPhase.T_90: {
            "temperature_celsius": 22.0,
            "rain_probability": 15.0,
            "wind_speed_kmh": 12.0,
            "lightning_detected": False,
            "visibility_meters": 9000.0,
            "match_phase": MatchPhase.T_90,
        },
        MatchPhase.T_60: {
            "temperature_celsius": 20.0,
            "rain_probability": 40.0,
            "wind_speed_kmh": 15.0,
            "lightning_detected": False,
            "visibility_meters": 7000.0,
            "match_phase": MatchPhase.T_60,
        },
        MatchPhase.T_30: {
            "temperature_celsius": 18.0,
            "rain_probability": 65.0,
            "wind_speed_kmh": 25.0,
            "lightning_detected": False,
            "visibility_meters": 6000.0,
            "match_phase": MatchPhase.T_30,
        },
        MatchPhase.KICKOFF: {
            "temperature_celsius": 17.0,
            "rain_probability": 50.0,
            "wind_speed_kmh": 18.0,
            "lightning_detected": False,
            "visibility_meters": 8000.0,
            "match_phase": MatchPhase.KICKOFF,
        },
        MatchPhase.HALFTIME: {
            "temperature_celsius": 16.0,
            "rain_probability": 75.0,
            "wind_speed_kmh": 22.0,
            "lightning_detected": False,
            "visibility_meters": 5500.0,
            "match_phase": MatchPhase.HALFTIME,
        },
        MatchPhase.RAIN_EVENT: {
            "temperature_celsius": 14.0,
            "rain_probability": 95.0,
            "wind_speed_kmh": 35.0,
            "lightning_detected": True,
            "visibility_meters": 800.0,
            "match_phase": MatchPhase.RAIN_EVENT,
        },
        MatchPhase.FULLTIME: {
            "temperature_celsius": 15.0,
            "rain_probability": 35.0,
            "wind_speed_kmh": 48.0,
            "lightning_detected": False,
            "visibility_meters": 7500.0,
            "match_phase": MatchPhase.FULLTIME,
        },
    }

    def generate(self, match_phase: MatchPhase) -> WeatherInput:
        """Generates deterministic WeatherInput for the specified match phase.

        Args:
            match_phase: The MatchPhase enum value (e.g., MatchPhase.T_120).

        Returns:
            A WeatherInput object populated with deterministic telemetry.

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
        return WeatherInput(**profile)
