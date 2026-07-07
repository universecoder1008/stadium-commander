"""Constants for the volunteer analyzer and simulator.

Contains threshold limits and baseline variables used for deterministic evaluation
of volunteer coverage, response times, request loads, and utilization rates.
"""

# Coverage thresholds in percent
LOW_COVERAGE_THRESHOLD = 50.0
MEDIUM_COVERAGE_THRESHOLD = 80.0

# Response time thresholds in minutes
RESPONSE_TIME_MEDIUM_THRESHOLD = 5.0
RESPONSE_TIME_HIGH_THRESHOLD = 15.0

# Utilization thresholds in percent
UTILIZATION_MEDIUM_THRESHOLD = 40.0
UTILIZATION_HIGH_THRESHOLD = 80.0

# Request load thresholds (number of active requests)
REQUEST_LOAD_MEDIUM_THRESHOLD = 10
REQUEST_LOAD_HIGH_THRESHOLD = 30

# Total expected telemetry fields in VolunteerInput
TOTAL_VOLUNTEER_TELEMETRY_FIELDS = 7
