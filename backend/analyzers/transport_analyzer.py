"""Transport Analyzer for Stadium Commander.

Evaluates transport telemetry to calculate overall risk and predictions.
"""

from typing import List, Optional
from analyzers.base_analyzer import BaseAnalyzer
from models.common import RiskLevel
from models.transport_schema import (
    TransportInput,
    TransportResponse,
    TransportPrediction
)
from config.transport_constants import (
    PARKING_MEDIUM_THRESHOLD,
    PARKING_HIGH_THRESHOLD,
    DELAY_MEDIUM_THRESHOLD,
    DELAY_HIGH_THRESHOLD,
    BASE_TRANSIT_TIME,
    TOTAL_TELEMETRY_FIELDS
)


class TransportAnalyzer(BaseAnalyzer):
    """Analyzer for evaluating football stadium transportation operations."""

    def analyze(self, input_data: TransportInput) -> TransportResponse:
        """Analyzes the current transport telemetry to determine risk levels and arrival predictions."""
        reasoning: List[str] = []

        # 1. Calculate confidence based on input completeness using the inherited method
        fields = [
            input_data.parking_capacity,
            input_data.parking_occupied,
            input_data.metro_expected,
            input_data.metro_arrived,
            input_data.metro_delay_minutes,
            input_data.buses_expected,
            input_data.buses_arrived,
            input_data.bus_delay_minutes,
            input_data.match_phase
        ]
        confidence = self.calculate_confidence(fields, TOTAL_TELEMETRY_FIELDS, reasoning)

        # 2. Analyze Parking Occupancy
        parking_pct, parking_status = self._analyze_parking(input_data, reasoning)

        # 3. Analyze Metro Delay
        metro_status = self._analyze_metro(input_data, reasoning)

        # 4. Analyze Bus Delay
        bus_status = self._analyze_bus(input_data, reasoning)

        # 5. Determine Overall Risk
        overall_risk = self._determine_overall_risk(
            parking_status, metro_status, bus_status, reasoning
        )

        # 6. Predict Spectator Arrivals
        arrival_pred = self._predict_arrivals(input_data, reasoning)

        return TransportResponse(
            risk=overall_risk,
            confidence=confidence,
            parking_occupancy_percent=parking_pct,
            metro_status=metro_status,
            bus_status=bus_status,
            arrival_prediction=arrival_pred,
            reasoning=reasoning
        )

    def _analyze_parking(self, input_data: TransportInput, reasoning: List[str]) -> tuple[float, RiskLevel]:
        """Calculates parking occupancy percentage and determines its risk status."""
        cap = input_data.parking_capacity
        occ = input_data.parking_occupied

        if cap is None or occ is None:
            reasoning.append("Parking telemetry is incomplete. Risk evaluated as LOW due to missing data.")
            return 0.0, RiskLevel.LOW

        if cap == 0:
            reasoning.append("Parking capacity is reported as 0. Risk evaluated as LOW.")
            return 0.0, RiskLevel.LOW

        pct = round((occ / cap) * 100, 1)

        if pct < PARKING_MEDIUM_THRESHOLD:
            status = RiskLevel.LOW
        elif pct <= PARKING_HIGH_THRESHOLD:
            status = RiskLevel.MEDIUM
        else:
            status = RiskLevel.HIGH

        reasoning.append(
            f"Parking occupancy is {pct}% (Occupied: {occ}, Capacity: {cap}). "
            f"Risk evaluated as {status.value}."
        )
        return pct, status

    def _analyze_delay(self, delay_minutes: Optional[int]) -> RiskLevel:
        """Determines risk level from delay minutes."""
        if delay_minutes is None:
            return RiskLevel.LOW

        if delay_minutes < DELAY_MEDIUM_THRESHOLD:
            return RiskLevel.LOW
        elif delay_minutes <= DELAY_HIGH_THRESHOLD:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    def _analyze_metro(self, input_data: TransportInput, reasoning: List[str]) -> RiskLevel:
        """Determines risk status for Metro arrivals based on delays."""
        delay = input_data.metro_delay_minutes

        if delay is None:
            reasoning.append("Metro delay telemetry is missing. Risk evaluated as LOW.")
            return RiskLevel.LOW

        status = self._analyze_delay(delay)
        reasoning.append(
            f"Metro delay is {delay} minutes. Risk evaluated as {status.value}."
        )
        return status

    def _analyze_bus(self, input_data: TransportInput, reasoning: List[str]) -> RiskLevel:
        """Determines risk status for Bus arrivals based on delays."""
        delay = input_data.bus_delay_minutes

        if delay is None:
            reasoning.append("Bus delay telemetry is missing. Risk evaluated as LOW.")
            return RiskLevel.LOW

        status = self._analyze_delay(delay)
        reasoning.append(
            f"Bus delay is {delay} minutes. Risk evaluated as {status.value}."
        )
        return status

    def _determine_overall_risk(
        self,
        parking_status: RiskLevel,
        metro_status: RiskLevel,
        bus_status: RiskLevel,
        reasoning: List[str]
    ) -> RiskLevel:
        """Combines component risks into an overall risk classification where HIGH dominates."""
        statuses = [parking_status, metro_status, bus_status]

        if RiskLevel.HIGH in statuses:
            overall = RiskLevel.HIGH
            reasons = []
            if parking_status == RiskLevel.HIGH:
                reasons.append("HIGH parking occupancy")
            if metro_status == RiskLevel.HIGH:
                reasons.append("HIGH metro delay")
            if bus_status == RiskLevel.HIGH:
                reasons.append("HIGH bus delay")
            reasoning.append(
                f"Overall transport risk is HIGH because high-risk indicators dominate: {', '.join(reasons)}."
            )
        elif RiskLevel.MEDIUM in statuses:
            overall = RiskLevel.MEDIUM
            reasons = []
            if parking_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM parking occupancy")
            if metro_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM metro delay")
            if bus_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM bus delay")
            reasoning.append(
                f"Overall transport risk is MEDIUM because medium-risk indicators are present: {', '.join(reasons)}."
            )
        else:
            overall = RiskLevel.LOW
            reasoning.append("Overall transport risk is LOW because all monitored factors are low risk.")

        return overall

    def _predict_arrivals(self, input_data: TransportInput, reasoning: List[str]) -> TransportPrediction:
        """Predicts remaining spectators and estimates travel time considering transit delays."""
        m_exp = input_data.metro_expected or 0
        m_arr = input_data.metro_arrived or 0
        m_rem = max(0, m_exp - m_arr)

        b_exp = input_data.buses_expected or 0
        b_arr = input_data.buses_arrived or 0
        b_rem = max(0, b_exp - b_arr)

        remaining_spectators = m_rem + b_rem

        if remaining_spectators == 0:
            eta = 0
            reasoning.append(
                "Arrival prediction: All expected spectators have arrived. Estimated remaining transit time is 0 minutes."
            )
        else:
            active_delays = []
            if m_rem > 0:
                active_delays.append(input_data.metro_delay_minutes or 0)
            if b_rem > 0:
                active_delays.append(input_data.bus_delay_minutes or 0)

            max_active_delay = max(active_delays) if active_delays else 0
            eta = BASE_TRANSIT_TIME + max_active_delay
            
            reasoning.append(
                f"Arrival prediction: {remaining_spectators} spectators remaining to arrive "
                f"(Metro: {m_rem}, Bus: {b_rem}). Estimated remaining transit time is {eta} minutes "
                f"(based on baseline of {BASE_TRANSIT_TIME} minutes and peak active delay of {max_active_delay} minutes)."
            )

        return TransportPrediction(
            remaining_spectators=remaining_spectators,
            estimated_arrival_minutes=eta
        )