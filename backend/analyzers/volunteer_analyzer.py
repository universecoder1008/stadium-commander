"""Volunteer Analyzer for Stadium Commander.

This module evaluates volunteer coordination telemetry deterministically to calculate
overall operational risk levels, expected volunteer shortages, and action recommendations.

Purpose:
    Provide stadium operators with a deterministic, real-time assessment of volunteer
    utilization, coverage, request load, and dispatch response times, without using AI.

Inputs:
    - VolunteerInput: A Pydantic model containing available/total volunteer counts,
      coverage percentages, response times, request loads, and match phase.

Outputs:
    - VolunteerResponse: Structured risk classifications (LOW, MEDIUM, HIGH) for volunteer parameters,
      float confidence (0.0 to 1.0), volunteer shortage predictions, redeployment guidelines,
      and detailed step-by-step reasoning.

Deterministic Guarantees:
    - Every calculation is based on pure mathematical logic and predefined static thresholds.
    - Overall risk is derived using high dominance (HIGH > MEDIUM > LOW).
    - Identical inputs will guarantee identical outputs.

AI Usage:
    - This code is 100% deterministic and runs entirely locally. It does not use Gemini or
      any other LLMs.
"""

from typing import List, Optional
from analyzers.base_analyzer import BaseAnalyzer
from models.common import RiskLevel, MatchPhase
from models.volunteer_schema import (
    VolunteerInput,
    VolunteerResponse,
    VolunteerPrediction
)
from config.volunteer_constants import (
    LOW_COVERAGE_THRESHOLD,
    MEDIUM_COVERAGE_THRESHOLD,
    RESPONSE_TIME_MEDIUM_THRESHOLD,
    RESPONSE_TIME_HIGH_THRESHOLD,
    UTILIZATION_MEDIUM_THRESHOLD,
    UTILIZATION_HIGH_THRESHOLD,
    REQUEST_LOAD_MEDIUM_THRESHOLD,
    REQUEST_LOAD_HIGH_THRESHOLD,
    TOTAL_VOLUNTEER_TELEMETRY_FIELDS
)


class VolunteerAnalyzer(BaseAnalyzer):
    """Analyzer for evaluating football stadium volunteer operations.
    
    Performs deterministic calculations, threshold validations, and predictive
    assessments on volunteer telemetry data.
    """

    def analyze(self, input_data: VolunteerInput) -> VolunteerResponse:
        """Analyzes the current volunteer telemetry to determine risk levels and recommendations.

        Args:
            input_data: A VolunteerInput instance containing telemetry data.

        Returns:
            A VolunteerResponse containing computed risk, predictions, and reasoning.
        """
        reasoning: List[str] = []

        # 1. Calculate confidence based on input completeness (float 0.0 - 1.0)
        fields = [
            input_data.available_volunteers,
            input_data.total_volunteers,
            input_data.zone_assignments,
            input_data.zone_coverage_percent,
            input_data.average_response_time_minutes,
            input_data.active_requests,
            input_data.match_phase
        ]
        confidence = self.calculate_confidence(fields, TOTAL_VOLUNTEER_TELEMETRY_FIELDS, reasoning)

        # 2. Analyze Volunteer Utilization
        util_pct, util_status = self._analyze_utilization(input_data, reasoning)

        # 3. Analyze Coverage Risk
        coverage_pct, coverage_status = self._analyze_coverage(input_data, reasoning)

        # 4. Analyze Response Time Risk
        response_status = self._analyze_response_time(input_data, reasoning)

        # 5. Analyze Request Load Risk
        request_status = self._analyze_request_load(input_data, reasoning)

        # 6. Determine Overall Risk
        overall_risk = self._determine_overall_risk(
            util_status, coverage_status, response_status, request_status, reasoning
        )

        # 7. Generate Volunteer Predictions and Recommendations
        prediction = self._generate_prediction(input_data, reasoning)

        return VolunteerResponse(
            risk=overall_risk,
            confidence=confidence,
            volunteer_utilization_percent=util_pct,
            coverage_percent=coverage_pct,
            prediction=prediction,
            reasoning=reasoning
        )

    def _analyze_utilization(self, input_data: VolunteerInput, reasoning: List[str]) -> tuple[float, RiskLevel]:
        """Calculates volunteer utilization and maps it to a risk level."""
        avail = input_data.available_volunteers
        total = input_data.total_volunteers

        if avail is None or total is None:
            reasoning.append("Volunteer capacity telemetry is incomplete. Risk evaluated as LOW due to missing data.")
            return 0.0, RiskLevel.LOW

        if total == 0:
            reasoning.append("Total volunteer capacity is reported as 0. Risk evaluated as LOW.")
            return 0.0, RiskLevel.LOW

        in_use = total - avail
        pct = round((in_use / total) * 100, 1)

        if pct < UTILIZATION_MEDIUM_THRESHOLD:
            status = RiskLevel.LOW
        elif pct <= UTILIZATION_HIGH_THRESHOLD:
            status = RiskLevel.MEDIUM
        else:
            status = RiskLevel.HIGH

        reasoning.append(
            f"Volunteer utilization is {pct}% (In Use: {in_use}, Total: {total}). "
            f"Risk evaluated as {status.value}."
        )
        return pct, status

    def _analyze_coverage(self, input_data: VolunteerInput, reasoning: List[str]) -> tuple[float, RiskLevel]:
        """Maps zone coverage percentage to a risk level."""
        cov = input_data.zone_coverage_percent

        if cov is None:
            reasoning.append("Zone coverage telemetry is missing. Risk evaluated as LOW due to missing data.")
            return 0.0, RiskLevel.LOW

        # Note: Lower coverage means HIGHER risk
        if cov < LOW_COVERAGE_THRESHOLD:
            status = RiskLevel.HIGH
        elif cov <= MEDIUM_COVERAGE_THRESHOLD:
            status = RiskLevel.MEDIUM
        else:
            status = RiskLevel.LOW

        reasoning.append(
            f"Zone coverage is {cov}% (Medium threshold: {MEDIUM_COVERAGE_THRESHOLD}%, Low threshold: {LOW_COVERAGE_THRESHOLD}%). "
            f"Risk evaluated as {status.value}."
        )
        return cov, status

    def _analyze_response_time(self, input_data: VolunteerInput, reasoning: List[str]) -> RiskLevel:
        """Determines risk status for response times based on thresholds."""
        resp = input_data.average_response_time_minutes

        if resp is None:
            reasoning.append("Response time telemetry is missing. Risk evaluated as LOW.")
            return RiskLevel.LOW

        if resp < RESPONSE_TIME_MEDIUM_THRESHOLD:
            status = RiskLevel.LOW
        elif resp <= RESPONSE_TIME_HIGH_THRESHOLD:
            status = RiskLevel.MEDIUM
        else:
            status = RiskLevel.HIGH

        reasoning.append(
            f"Average dispatch response time is {resp} minutes. Risk evaluated as {status.value}."
        )
        return status

    def _analyze_request_load(self, input_data: VolunteerInput, reasoning: List[str]) -> RiskLevel:
        """Determines risk status for active requests load based on thresholds."""
        req = input_data.active_requests

        if req is None:
            reasoning.append("Active requests telemetry is missing. Risk evaluated as LOW.")
            return RiskLevel.LOW

        if req < REQUEST_LOAD_MEDIUM_THRESHOLD:
            status = RiskLevel.LOW
        elif req <= REQUEST_LOAD_HIGH_THRESHOLD:
            status = RiskLevel.MEDIUM
        else:
            status = RiskLevel.HIGH

        reasoning.append(
            f"Active requests count is {req}. Risk evaluated as {status.value}."
        )
        return status

    def _determine_overall_risk(
        self,
        util_status: RiskLevel,
        coverage_status: RiskLevel,
        response_status: RiskLevel,
        request_status: RiskLevel,
        reasoning: List[str]
    ) -> RiskLevel:
        """Combines component risks into overall risk level where HIGH dominates."""
        statuses = [util_status, coverage_status, response_status, request_status]

        if RiskLevel.HIGH in statuses:
            overall = RiskLevel.HIGH
            reasons = []
            if util_status == RiskLevel.HIGH:
                reasons.append("HIGH volunteer utilization")
            if coverage_status == RiskLevel.HIGH:
                reasons.append("HIGH coverage gap")
            if response_status == RiskLevel.HIGH:
                reasons.append("HIGH response delay")
            if request_status == RiskLevel.HIGH:
                reasons.append("HIGH request load")
            reasoning.append(
                f"Overall volunteer risk is HIGH due to critical indicators: {', '.join(reasons)}."
            )
        elif RiskLevel.MEDIUM in statuses:
            overall = RiskLevel.MEDIUM
            reasons = []
            if util_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM volunteer utilization")
            if coverage_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM coverage gap")
            if response_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM response delay")
            if request_status == RiskLevel.MEDIUM:
                reasons.append("MEDIUM request load")
            reasoning.append(
                f"Overall volunteer risk is MEDIUM due to moderate indicators: {', '.join(reasons)}."
            )
        else:
            overall = RiskLevel.LOW
            reasoning.append("Overall volunteer risk is LOW because all monitored factors are low risk.")

        return overall

    def _generate_prediction(self, input_data: VolunteerInput, reasoning: List[str]) -> VolunteerPrediction:
        """Generates deterministic predictions and recommended redeployments."""
        req = input_data.active_requests or 0
        avail = input_data.available_volunteers or 0
        base_resp = input_data.average_response_time_minutes or 2.0
        phase = input_data.match_phase

        # 1. Calculate shortage: assume 2 volunteers are needed per request
        required_volunteers = req * 2
        shortage = max(0, required_volunteers - avail)

        # 2. Predict response time increase due to shortage
        if shortage > 0:
            pred_response_time = round(base_resp + (shortage * 0.5), 1)
        else:
            pred_response_time = round(base_resp, 1)

        # 3. Formulate redeployment action based on match phase and shortages
        if shortage > 0:
            if phase == MatchPhase.RAIN_EVENT:
                redeploy = "Move outdoor volunteers indoors and deploy reserve volunteers to covered concourses"
            elif phase in [MatchPhase.T_30, MatchPhase.KICKOFF]:
                redeploy = "Move 5 volunteers from Zone C to Zone A near Gate B security queues"
            elif phase == MatchPhase.FULLTIME:
                redeploy = "Deploy reserve volunteers to main exits and transit gates for egress management"
            else:
                redeploy = "Deploy reserve volunteers to active zones"
        else:
            redeploy = "Proceed with current zone allocations"

        reasoning.append(
            f"Volunteer predictions: Expected shortage: {shortage} volunteers. "
            f"Predicted dispatch response time: {pred_response_time} minutes. "
            f"Recommendation: '{redeploy}'."
        )

        return VolunteerPrediction(
            expected_shortage=shortage,
            recommended_redeployment=redeploy,
            predicted_response_time=pred_response_time
        )
