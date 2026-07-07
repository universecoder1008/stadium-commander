"""Crowd Analyzer for Stadium Commander.

Evaluates gate occupancy levels deterministically to categorize crowd control risks.
"""

from analyzers.base_analyzer import BaseAnalyzer
from models.crowd_schema import CrowdResponse, Prediction


class CrowdAnalyzer(BaseAnalyzer):
    """Analyzer for evaluating crowd risk and gate entry rate levels."""

    def analyze(self, stadium) -> CrowdResponse:
        """Deterministically analyzes the stadium gates occupancy to assess crowd risks."""
        highest = max(
            stadium.gates,
            key=lambda gate: gate.occupancy
        )

        if highest.occupancy >= 90:
            risk = "CRITICAL"
            confidence = 98

        elif highest.occupancy >= 75:
            risk = "HIGH"
            confidence = 90

        elif highest.occupancy >= 50:
            risk = "MEDIUM"
            confidence = 80

        else:
            risk = "LOW"
            confidence = 70

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