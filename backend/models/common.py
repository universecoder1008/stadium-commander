"""Common data models and enums for Stadium Commander.

Contains shared enums used across schemas, analyzers, and simulators to ensure
type safety and consistency throughout the platform.
"""

from enum import Enum


class RiskLevel(str, Enum):
    """Enumeration representing operational risk levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class MatchPhase(str, Enum):
    """Enumeration representing football match phases."""
    T_120 = "T-120"
    T_90 = "T-90"
    T_60 = "T-60"
    T_30 = "T-30"
    KICKOFF = "Kickoff"
    HALFTIME = "Halftime"
    FULLTIME = "Full-time"
    RAIN_EVENT = "Rain Event"
