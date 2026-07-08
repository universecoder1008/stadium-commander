"""Crowd Analyzer for Stadium Commander.

Evaluates gate occupancy levels deterministically to categorize crowd control risks.
"""

from analyzers.base_analyzer import BaseAnalyzer
from models.crowd_schema import CrowdResponse, Prediction
from models.stadium_input import StadiumInput
from config.crowd_constants import (
    CROWD_MEDIUM_THRESHOLD,
    CROWD_HIGH_THRESHOLD,
    CROWD_CRITICAL_THRESHOLD,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_HIGH,
    CONFIDENCE_CRITICAL
)


class CrowdAnalyzer(BaseAnalyzer):
    """Analyzer for evaluating crowd risk and gate entry rate levels."""

    def analyze(self, stadium: StadiumInput) -> CrowdResponse:
        """Deterministically analyzes the stadium gates occupancy to assess crowd risks.

        Args:
            stadium: The primary StadiumInput telemetry package.

        Returns:
            A validated CrowdResponse object detailing risk status.
        """
        if not stadium.gates:
            return CrowdResponse(
                risk="LOW",
                confidence=CONFIDENCE_LOW,
                predictions=[],
                reasoning=["No active gates telemetry received."]
            )

        highest = max(
            stadium.gates,
            key=lambda gate: gate.occupancy
        )

        if highest.occupancy >= CROWD_CRITICAL_THRESHOLD:
            risk = "CRITICAL"
            confidence = CONFIDENCE_CRITICAL

        elif highest.occupancy >= CROWD_HIGH_THRESHOLD:
            risk = "HIGH"
            confidence = CONFIDENCE_HIGH

        elif highest.occupancy >= CROWD_MEDIUM_THRESHOLD:
            risk = "MEDIUM"
            confidence = CONFIDENCE_MEDIUM

        else:
            risk = "LOW"
            confidence = CONFIDENCE_LOW

        return CrowdResponse(
            risk=risk,
            confidence=confidence,
            predictions=[
                Prediction(
                    gate=highest.gate,
                    issue="High crowd density",
                    eta_minutes=5
                )
            ],
            reasoning=[
                f"Highest occupancy is {highest.occupancy}%."
            ]
        )