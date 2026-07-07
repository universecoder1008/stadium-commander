from models.crowd_schema import CrowdResponse, Prediction


class CrowdAnalyzer:

    def analyze(self, stadium):

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