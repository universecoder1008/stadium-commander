"""Weather Analyzer for Stadium Commander.

Evaluates weather telemetry deterministically to calculate overall risk levels,
expected delays, and action recommendations.
"""

from typing import List, Optional
from analyzers.base_analyzer import BaseAnalyzer
from models.common import RiskLevel, MatchPhase
from models.weather_schema import (
    WeatherInput,
    WeatherResponse,
    WeatherPrediction
)
from config.weather_constants import (
    RAIN_MEDIUM_THRESHOLD,
    RAIN_HIGH_THRESHOLD,
    WIND_MEDIUM_THRESHOLD,
    WIND_HIGH_THRESHOLD,
    VISIBILITY_HIGH_RISK_LIMIT,
    VISIBILITY_MEDIUM_RISK_LIMIT,
    LIGHTNING_DELAY_MINUTES,
    RAIN_DELAY_MINUTES,
    WIND_DELAY_MINUTES,
    MEDIUM_DELAY_MINUTES,
    LOW_DELAY_MINUTES,
    TOTAL_WEATHER_TELEMETRY_FIELDS
)


class WeatherAnalyzer(BaseAnalyzer):
    """Analyzer for evaluating football stadium weather operations."""

    def analyze(self, input_data: WeatherInput) -> WeatherResponse:
        """Analyzes the current weather telemetry to determine risk levels and recommendations."""
        reasoning: List[str] = []

        # 1. Calculate confidence based on input completeness using the inherited method
        fields = [
            input_data.temperature_celsius,
            input_data.rain_probability,
            input_data.wind_speed_kmh,
            input_data.lightning_detected,
            input_data.visibility_meters,
            input_data.match_phase
        ]
        confidence = self.calculate_confidence(fields, TOTAL_WEATHER_TELEMETRY_FIELDS, reasoning)

        # 2. Analyze Rain Risk
        rain_status = self._analyze_rain(input_data, reasoning)

        # 3. Analyze Wind Risk
        wind_status = self._analyze_wind(input_data, reasoning)

        # 4. Analyze Visibility Risk
        visibility_status = self._analyze_visibility(input_data, reasoning)

        # 5. Determine Overall Risk (considering lightning override)
        overall_risk = self._determine_overall_risk(
            rain_status, wind_status, visibility_status, input_data, reasoning
        )

        # 6. Generate Weather Predictions and Recommendations
        prediction = self._generate_prediction(input_data, reasoning)

        return WeatherResponse(
            risk=overall_risk,
            confidence=confidence,
            weather_status=overall_risk,
            prediction=prediction,
            reasoning=reasoning
        )

    def _analyze_rain(self, input_data: WeatherInput, reasoning: List[str]) -> RiskLevel:
        """Determines risk status for rain probability based on thresholds."""
        rain = input_data.rain_probability

        if rain is None:
            reasoning.append("Rain telemetry is missing. Risk evaluated as LOW.")
            return RiskLevel.LOW

        if rain < RAIN_MEDIUM_THRESHOLD:
            status = RiskLevel.LOW
        elif rain <= RAIN_HIGH_THRESHOLD:
            status = RiskLevel.MEDIUM
        else:
            status = RiskLevel.HIGH

        reasoning.append(
            f"Rain probability is {rain}% (Medium threshold: {RAIN_MEDIUM_THRESHOLD}%, High threshold: {RAIN_HIGH_THRESHOLD}%). "
            f"Risk evaluated as {status.value}."
        )
        return status

    def _analyze_wind(self, input_data: WeatherInput, reasoning: List[str]) -> RiskLevel:
        """Determines risk status for wind speed based on thresholds."""
        wind = input_data.wind_speed_kmh

        if wind is None:
            reasoning.append("Wind speed telemetry is missing. Risk evaluated as LOW.")
            return RiskLevel.LOW

        if wind < WIND_MEDIUM_THRESHOLD:
            status = RiskLevel.LOW
        elif wind <= WIND_HIGH_THRESHOLD:
            status = RiskLevel.MEDIUM
        else:
            status = RiskLevel.HIGH

        reasoning.append(
            f"Wind speed is {wind} km/h (Medium threshold: {WIND_MEDIUM_THRESHOLD} km/h, High threshold: {WIND_HIGH_THRESHOLD} km/h). "
            f"Risk evaluated as {status.value}."
        )
        return status

    def _analyze_visibility(self, input_data: WeatherInput, reasoning: List[str]) -> RiskLevel:
        """Determines risk status for horizontal visibility based on thresholds."""
        vis = input_data.visibility_meters

        if vis is None:
            reasoning.append("Visibility telemetry is missing. Risk evaluated as LOW.")
            return RiskLevel.LOW

        if vis < VISIBILITY_HIGH_RISK_LIMIT:
            status = RiskLevel.HIGH
        elif vis <= VISIBILITY_MEDIUM_RISK_LIMIT:
            status = RiskLevel.MEDIUM
        else:
            status = RiskLevel.LOW

        reasoning.append(
            f"Horizontal visibility is {vis} meters (Medium threshold: {VISIBILITY_MEDIUM_RISK_LIMIT}m, High threshold: {VISIBILITY_HIGH_RISK_LIMIT}m). "
            f"Risk evaluated as {status.value}."
        )
        return status

    def _determine_overall_risk(
        self,
        rain_status: RiskLevel,
        wind_status: RiskLevel,
        visibility_status: RiskLevel,
        input_data: WeatherInput,
        reasoning: List[str]
    ) -> RiskLevel:
        """Combines component risks with lightning overrides to decide overall weather risk."""
        lightning = input_data.lightning_detected or False
        if lightning:
            reasoning.append(
                "OVERRIDE: Active lightning detected in the stadium vicinity. "
                "Overall weather risk is immediately evaluated as HIGH."
            )
            return RiskLevel.HIGH

        statuses = [rain_status, wind_status, visibility_status]

        if RiskLevel.HIGH in statuses:
            overall = RiskLevel.HIGH
            reasons = []
            if rain_status == RiskLevel.HIGH:
                reasons.append("HIGH rain probability")
            if wind_status == RiskLevel.HIGH:
                reasons.append("HIGH wind speeds")
            if visibility_status == RiskLevel.HIGH:
                reasons.append("HIGH visibility risk")
            reasoning.append(
                f"Overall weather risk is HIGH due to critical indicators: {', '.join(reasons)}."
            )
        elif RiskLevel.MEDIUM in statuses:
            overall = RiskLevel.MEDIUM
            reasons = []
            if rain_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM rain probability")
            if wind_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM wind speeds")
            if visibility_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM visibility risk")
            reasoning.append(
                f"Overall weather risk is MEDIUM due to moderate indicators: {', '.join(reasons)}."
            )
        else:
            overall = RiskLevel.LOW
            reasoning.append("Overall weather risk is LOW because all monitored factors are low risk.")

        return overall

    def _generate_prediction(self, input_data: WeatherInput, reasoning: List[str]) -> WeatherPrediction:
        """Generates deterministic prediction outputs, delay estimates, and actions."""
        lightning = input_data.lightning_detected or False
        rain = input_data.rain_probability or 0.0
        wind = input_data.wind_speed_kmh or 0.0
        vis = input_data.visibility_meters

        if lightning:
            impact = "Critical: Outdoor operations suspended due to lightning strike hazard"
            delay = LIGHTNING_DELAY_MINUTES
            recommendation = "Pause outdoor operations, evacuate spectators to covered concourses immediately"
        elif rain > RAIN_HIGH_THRESHOLD or (vis is not None and vis < VISIBILITY_HIGH_RISK_LIMIT):
            impact = "High: Severe rain and low visibility causing queue congestion"
            delay = RAIN_DELAY_MINUTES
            recommendation = "Open additional covered gates, activate high-intensity stadium lighting"
        elif wind > WIND_HIGH_THRESHOLD:
            impact = "High: High wind speeds causing hazard for structural fixtures"
            delay = WIND_DELAY_MINUTES
            recommendation = "Implement temporary banner restrictions and secure loose structures"
        elif rain > RAIN_MEDIUM_THRESHOLD or wind > WIND_MEDIUM_THRESHOLD or (vis is not None and vis <= VISIBILITY_MEDIUM_RISK_LIMIT):
            impact = "Medium: Light rain and moderate winds causing minor delays"
            delay = MEDIUM_DELAY_MINUTES
            recommendation = "Monitor weather conditions, advise fans to carry ponchos"
        else:
            impact = "Low: Clear conditions, normal operations"
            delay = LOW_DELAY_MINUTES
            recommendation = "Proceed with normal matchday operations"

        reasoning.append(
            f"Weather predictions: Operational impact: '{impact}'. "
            f"Expected delay: {delay} minutes. Action: '{recommendation}'."
        )

        return WeatherPrediction(
            expected_operational_impact=impact,
            expected_delay_minutes=delay,
            recommendation=recommendation
        )
