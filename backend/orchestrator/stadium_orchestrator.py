"""Stadium Orchestrator for Stadium Commander.

This module is responsible for orchestrating all Python analyzers, executing them
sequentially, measuring performance, handling exceptions gracefully, and producing
a CombinedSituationReport.
"""

import time
import logging
from typing import Any, List, Dict

from models.stadium_input import StadiumInput
from models.situation_report import CombinedSituationReport, SystemStatus
from models.common import RiskLevel
from models.transport_schema import TransportInput

# Setup logger for the orchestrator
logger = logging.getLogger("stadium_commander.orchestrator")


class StadiumOrchestrator:
    """Orchestrator for managing individual analyzers and aggregating results."""

    def __init__(
        self,
        crowd_analyzer: Any,
        transport_analyzer: Any,
        medical_analyzer: Any,
        weather_analyzer: Any,
        volunteer_analyzer: Any
    ):
        """Initializes the orchestrator with analyzer instances via dependency injection.

        Args:
            crowd_analyzer: The CrowdAnalyzer instance.
            transport_analyzer: The TransportAnalyzer instance.
            medical_analyzer: The MedicalAnalyzer instance.
            weather_analyzer: The WeatherAnalyzer instance.
            volunteer_analyzer: The VolunteerAnalyzer instance.
        """
        self.crowd_analyzer = crowd_analyzer
        self.transport_analyzer = transport_analyzer
        self.medical_analyzer = medical_analyzer
        self.weather_analyzer = weather_analyzer
        self.volunteer_analyzer = volunteer_analyzer

    def analyze(self, stadium_data: StadiumInput) -> CombinedSituationReport:
        """Invokes each analyzer sequentially, handles exceptions, and aggregates results.

        Args:
            stadium_data: The main StadiumInput telemetry package.

        Returns:
            A CombinedSituationReport summarizing all subsystems.
        """
        logger.info("Starting overall stadium orchestration loop.")
        overall_start = time.perf_counter()

        analyzers_completed: List[str] = []
        analyzers_failed: Dict[str, str] = {}

        # 1. Run Crowd Analyzer
        crowd_res = None
        try:
            logger.info("Crowd Analyzer: execution started.")
            t_start = time.perf_counter()
            crowd_res = self.crowd_analyzer.analyze(stadium_data)
            t_end = time.perf_counter()
            elapsed_ms = (t_end - t_start) * 1000.0
            logger.info("Crowd Analyzer: execution finished. Processing time: %.2f ms.", elapsed_ms)
            analyzers_completed.append("crowd")
        except Exception as e:
            logger.exception("Crowd Analyzer: execution failed: %s", str(e))
            analyzers_failed["crowd"] = str(e)

        # 2. Run Transport Analyzer
        transport_res = None
        try:
            # Resolve the input telemetry model or fall back to mapping
            transport_in = stadium_data.transport_telemetry
            if transport_in is None:
                try:
                    occ = stadium_data.transport.parking.occupancy
                    avail = stadium_data.transport.parking.available_spots
                    transport_in = TransportInput(
                        parking_capacity=occ + avail,
                        parking_occupied=occ,
                        metro_expected=stadium_data.transport.metro.expected_passengers,
                        metro_arrived=0,
                        metro_delay_minutes=stadium_data.transport.metro.next_arrival_minutes,
                        buses_expected=0,
                        buses_arrived=0,
                        bus_delay_minutes=stadium_data.transport.bus.delay_minutes,
                        match_phase=stadium_data.match_phase
                    )
                except Exception:
                    pass

            if transport_in is not None:
                logger.info("Transport Analyzer: execution started.")
                t_start = time.perf_counter()
                transport_res = self.transport_analyzer.analyze(transport_in)
                t_end = time.perf_counter()
                elapsed_ms = (t_end - t_start) * 1000.0
                logger.info("Transport Analyzer: execution finished. Processing time: %.2f ms.", elapsed_ms)
                analyzers_completed.append("transport")
            else:
                logger.warning("Transport Analyzer: skipped due to missing transport telemetry.")
        except Exception as e:
            logger.exception("Transport Analyzer: execution failed: %s", str(e))
            analyzers_failed["transport"] = str(e)

        # 3. Run Medical Analyzer
        medical_res = None
        try:
            if stadium_data.medical is not None:
                logger.info("Medical Analyzer: execution started.")
                t_start = time.perf_counter()
                medical_res = self.medical_analyzer.analyze(stadium_data.medical)
                t_end = time.perf_counter()
                elapsed_ms = (t_end - t_start) * 1000.0
                logger.info("Medical Analyzer: execution finished. Processing time: %.2f ms.", elapsed_ms)
                analyzers_completed.append("medical")
            else:
                logger.warning("Medical Analyzer: skipped due to missing medical telemetry.")
        except Exception as e:
            logger.exception("Medical Analyzer: execution failed: %s", str(e))
            analyzers_failed["medical"] = str(e)

        # 4. Run Weather Analyzer
        weather_res = None
        try:
            if stadium_data.weather is not None:
                logger.info("Weather Analyzer: execution started.")
                t_start = time.perf_counter()
                weather_res = self.weather_analyzer.analyze(stadium_data.weather)
                t_end = time.perf_counter()
                elapsed_ms = (t_end - t_start) * 1000.0
                logger.info("Weather Analyzer: execution finished. Processing time: %.2f ms.", elapsed_ms)
                analyzers_completed.append("weather")
            else:
                logger.warning("Weather Analyzer: skipped due to missing weather telemetry.")
        except Exception as e:
            logger.exception("Weather Analyzer: execution failed: %s", str(e))
            analyzers_failed["weather"] = str(e)

        # 5. Run Volunteer Analyzer
        volunteer_res = None
        try:
            if stadium_data.volunteer is not None:
                logger.info("Volunteer Analyzer: execution started.")
                t_start = time.perf_counter()
                volunteer_res = self.volunteer_analyzer.analyze(stadium_data.volunteer)
                t_end = time.perf_counter()
                elapsed_ms = (t_end - t_start) * 1000.0
                logger.info("Volunteer Analyzer: execution finished. Processing time: %.2f ms.", elapsed_ms)
                analyzers_completed.append("volunteer")
            else:
                logger.warning("Volunteer Analyzer: skipped due to missing volunteer telemetry.")
        except Exception as e:
            logger.exception("Volunteer Analyzer: execution failed: %s", str(e))
            analyzers_failed["volunteer"] = str(e)

        # Calculate system-wide status enum
        system_status = self._calculate_system_status(
            crowd_res, transport_res, medical_res, weather_res, volunteer_res
        )

        overall_end = time.perf_counter()
        overall_duration_ms = (overall_end - overall_start) * 1000.0
        logger.info(
            "Overall stadium orchestration finished. Overall processing time: %.2f ms. System status: %s.",
            overall_duration_ms, system_status.value
        )

        return CombinedSituationReport(
            timestamp=stadium_data.current_time,
            match_phase=stadium_data.match_phase,
            crowd=crowd_res,
            transport=transport_res,
            medical=medical_res,
            weather=weather_res,
            volunteer=volunteer_res,
            system_status=system_status,
            analyzers_completed=analyzers_completed,
            analyzers_failed=analyzers_failed,
            processing_time_ms=overall_duration_ms
        )

    def _calculate_system_status(
        self,
        crowd: Any,
        transport: Any,
        medical: Any,
        weather: Any,
        volunteer: Any
    ) -> SystemStatus:
        """Determines system_status (CRITICAL, WARNING, NORMAL) based on component risks."""
        risks = []

        if crowd is not None:
            risks.append(crowd.risk)
        if transport is not None:
            risks.append(transport.risk)
        if medical is not None:
            risks.append(medical.risk)
        if weather is not None:
            risks.append(weather.risk)
        if volunteer is not None:
            risks.append(volunteer.risk)

        # Risk mapping rules
        is_critical = any(r in ("CRITICAL", "HIGH", RiskLevel.HIGH) for r in risks)
        if is_critical:
            return SystemStatus.CRITICAL

        is_warning = any(r in ("MEDIUM", RiskLevel.MEDIUM) for r in risks)
        if is_warning:
            return SystemStatus.WARNING

        return SystemStatus.NORMAL