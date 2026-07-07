"""Medical Analyzer for Stadium Commander.

Evaluates medical telemetry deterministically to calculate overall risk levels,
resource shortages, and dispatch time predictions.
"""

from typing import List, Optional
from analyzers.base_analyzer import BaseAnalyzer
from models.common import RiskLevel, MatchPhase
from models.medical_schema import (
    MedicalInput,
    MedicalResponse,
    MedicalPrediction
)
from config.medical_constants import (
    QUEUE_LOW_THRESHOLD,
    QUEUE_HIGH_THRESHOLD,
    RESPONSE_TIME_LOW_THRESHOLD,
    RESPONSE_TIME_HIGH_THRESHOLD,
    UTILIZATION_MEDIUM_THRESHOLD,
    UTILIZATION_HIGH_THRESHOLD,
    TOTAL_MEDICAL_TELEMETRY_FIELDS
)


class MedicalAnalyzer(BaseAnalyzer):
    """Analyzer for evaluating football stadium medical operations."""

    def analyze(self, input_data: MedicalInput) -> MedicalResponse:
        """Analyzes the current medical telemetry to determine risk levels and resource predictions."""
        reasoning: List[str] = []

        # 1. Calculate confidence based on input completeness using the inherited method
        fields = [
            input_data.active_incidents,
            input_data.critical_incidents,
            input_data.ambulances_available,
            input_data.ambulances_total,
            input_data.first_aid_queue,
            input_data.medical_staff_available,
            input_data.medical_staff_total,
            input_data.average_response_time_minutes,
            input_data.match_phase
        ]
        confidence = self.calculate_confidence(fields, TOTAL_MEDICAL_TELEMETRY_FIELDS, reasoning)

        # 2. Analyze resource utilizations
        amb_pct, amb_util_status = self._analyze_ambulance_utilization(input_data, reasoning)
        staff_pct, staff_util_status = self._analyze_staff_utilization(input_data, reasoning)

        # 3. Analyze Queue Risk
        queue_status = self._analyze_queue(input_data, reasoning)

        # 4. Analyze Response Time Risk
        response_status = self._analyze_response_time(input_data, reasoning)

        # 5. Determine Overall Risk (considering critical incidents)
        overall_risk = self._determine_overall_risk(
            queue_status, response_status, amb_util_status, staff_util_status, input_data, reasoning
        )

        # 6. Predict Future Incidents and Shortages
        prediction = self._predict_medical_needs(input_data, amb_pct, staff_pct, reasoning)

        return MedicalResponse(
            risk=overall_risk,
            confidence=confidence,
            ambulance_utilization_percent=amb_pct,
            medical_staff_utilization_percent=staff_pct,
            prediction=prediction,
            reasoning=reasoning
        )

    def _determine_utilization_risk(self, utilization_percent: float) -> RiskLevel:
        """Helper to classify utilization percentage into a risk level."""
        if utilization_percent < UTILIZATION_MEDIUM_THRESHOLD:
            return RiskLevel.LOW
        elif utilization_percent <= UTILIZATION_HIGH_THRESHOLD:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    def _analyze_ambulance_utilization(self, input_data: MedicalInput, reasoning: List[str]) -> tuple[float, RiskLevel]:
        """Calculates ambulance utilization and maps it to a risk level."""
        avail = input_data.ambulances_available
        total = input_data.ambulances_total

        if avail is None or total is None:
            reasoning.append("Ambulance telemetry is incomplete. Risk evaluated as LOW due to missing data.")
            return 0.0, RiskLevel.LOW

        if total == 0:
            reasoning.append("Total ambulance capacity is reported as 0. Risk evaluated as LOW.")
            return 0.0, RiskLevel.LOW

        in_use = total - avail
        pct = round((in_use / total) * 100, 1)
        status = self._determine_utilization_risk(pct)

        reasoning.append(
            f"Ambulance utilization is {pct}% (In Use: {in_use}, Total: {total}). "
            f"Risk evaluated as {status.value}."
        )
        return pct, status

    def _analyze_staff_utilization(self, input_data: MedicalInput, reasoning: List[str]) -> tuple[float, RiskLevel]:
        """Calculates medical staff utilization and maps it to a risk level."""
        avail = input_data.medical_staff_available
        total = input_data.medical_staff_total

        if avail is None or total is None:
            reasoning.append("Medical staff telemetry is incomplete. Risk evaluated as LOW due to missing data.")
            return 0.0, RiskLevel.LOW

        if total == 0:
            reasoning.append("Total medical staff capacity is reported as 0. Risk evaluated as LOW.")
            return 0.0, RiskLevel.LOW

        in_use = total - avail
        pct = round((in_use / total) * 100, 1)
        status = self._determine_utilization_risk(pct)

        reasoning.append(
            f"Medical staff utilization is {pct}% (In Use: {in_use}, Total: {total}). "
            f"Risk evaluated as {status.value}."
        )
        return pct, status

    def _analyze_queue(self, input_data: MedicalInput, reasoning: List[str]) -> RiskLevel:
        """Determines risk status for first aid queues based on thresholds."""
        queue = input_data.first_aid_queue

        if queue is None:
            reasoning.append("First aid queue telemetry is missing. Risk evaluated as LOW.")
            return RiskLevel.LOW

        if queue < QUEUE_LOW_THRESHOLD:
            status = RiskLevel.LOW
        elif queue <= QUEUE_HIGH_THRESHOLD:
            status = RiskLevel.MEDIUM
        else:
            status = RiskLevel.HIGH

        reasoning.append(
            f"First aid queue size is {queue}. Risk evaluated as {status.value}."
        )
        return status

    def _analyze_response_time(self, input_data: MedicalInput, reasoning: List[str]) -> RiskLevel:
        """Determines risk status for emergency dispatch times based on thresholds."""
        resp_time = input_data.average_response_time_minutes

        if resp_time is None:
            reasoning.append("Average response time telemetry is missing. Risk evaluated as LOW.")
            return RiskLevel.LOW

        if resp_time < RESPONSE_TIME_LOW_THRESHOLD:
            status = RiskLevel.LOW
        elif resp_time <= RESPONSE_TIME_HIGH_THRESHOLD:
            status = RiskLevel.MEDIUM
        else:
            status = RiskLevel.HIGH

        reasoning.append(
            f"Average response time is {resp_time} minutes. Risk evaluated as {status.value}."
        )
        return status

    def _determine_overall_risk(
        self,
        queue_status: RiskLevel,
        response_status: RiskLevel,
        amb_status: RiskLevel,
        staff_status: RiskLevel,
        input_data: MedicalInput,
        reasoning: List[str]
    ) -> RiskLevel:
        """Combines metrics and critical incident escalations to evaluate overall risk."""
        statuses = [queue_status, response_status, amb_status, staff_status]

        # Base overall risk is decided by high-dominance
        if RiskLevel.HIGH in statuses:
            base_risk = RiskLevel.HIGH
            reasons = []
            if queue_status == RiskLevel.HIGH:
                reasons.append("HIGH first aid queue")
            if response_status == RiskLevel.HIGH:
                reasons.append("HIGH response time")
            if amb_status == RiskLevel.HIGH:
                reasons.append("HIGH ambulance utilization")
            if staff_status == RiskLevel.HIGH:
                reasons.append("HIGH medical staff utilization")
            reasoning.append(
                f"Base overall risk is HIGH due to critical indicators: {', '.join(reasons)}."
            )
        elif RiskLevel.MEDIUM in statuses:
            base_risk = RiskLevel.MEDIUM
            reasons = []
            if queue_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM first aid queue")
            if response_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM response time")
            if amb_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM ambulance utilization")
            if staff_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM medical staff utilization")
            reasoning.append(
                f"Base overall risk is MEDIUM due to moderate indicators: {', '.join(reasons)}."
            )
        else:
            base_risk = RiskLevel.LOW
            reasoning.append("Base overall risk is LOW because all components are within safe thresholds.")

        # Escalate overall risk if critical incidents exist
        crit_incidents = input_data.critical_incidents or 0
        final_risk = base_risk

        if crit_incidents > 0:
            if base_risk == RiskLevel.LOW:
                final_risk = RiskLevel.MEDIUM
                reasoning.append(
                    f"Overall risk escalated from LOW to MEDIUM due to {crit_incidents} active critical incidents."
                )
            elif base_risk == RiskLevel.MEDIUM:
                final_risk = RiskLevel.HIGH
                reasoning.append(
                    f"Overall risk escalated from MEDIUM to HIGH due to {crit_incidents} active critical incidents."
                )
            else:
                reasoning.append(
                    f"Overall risk remains HIGH (already at maximum risk level with {crit_incidents} active critical incidents)."
                )

        return final_risk

    def _predict_medical_needs(
        self,
        input_data: MedicalInput,
        amb_util_percent: float,
        staff_util_percent: float,
        reasoning: List[str]
    ) -> MedicalPrediction:
        """Generates deterministic prediction metrics regarding future load and delays."""
        active = input_data.active_incidents or 0
        phase = input_data.match_phase

        # 1. Predict future incidents based on match phase
        if phase in [MatchPhase.T_60, MatchPhase.T_30, MatchPhase.FULLTIME, MatchPhase.RAIN_EVENT]:
            # Peak activity / hazard phases
            predicted_incidents = int(active * 1.5) + 3
            phase_type = "peak workload/hazard phase"
        else:
            # Low activity phases
            predicted_incidents = int(active * 1.1) + 1
            phase_type = "standard workload phase"

        # 2. Estimate response time delays
        base_resp = input_data.average_response_time_minutes or 2
        queue_len = input_data.first_aid_queue or 0
        added_time = 0

        if queue_len > QUEUE_HIGH_THRESHOLD:
            added_time += 5
        elif queue_len > QUEUE_LOW_THRESHOLD:
            added_time += 2

        if amb_util_percent > UTILIZATION_HIGH_THRESHOLD:
            added_time += 3

        est_response_time = base_resp + added_time

        # 3. Assess expected resource shortages
        staff_avail = input_data.medical_staff_available or 0
        shortage = (
            amb_util_percent > UTILIZATION_HIGH_THRESHOLD or
            staff_util_percent > UTILIZATION_HIGH_THRESHOLD or
            predicted_incidents > staff_avail
        )

        # Reasoning notes
        shortage_str = "YES" if shortage else "NO"
        reasoning.append(
            f"Medical predictions: Forecasted future incidents: {predicted_incidents} (multiplier applied for {phase_type}). "
            f"Expected resource shortage: {shortage_str}. Estimated response time: {est_response_time} minutes "
            f"(base: {base_resp}m, queue impact: +{added_time}m)."
        )

        return MedicalPrediction(
            predicted_incidents=predicted_incidents,
            resource_shortage=shortage,
            estimated_response_time=est_response_time
        )
