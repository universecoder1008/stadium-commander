"""Constants for the medical analyzer and simulator.

Contains threshold limits and baseline variables used for deterministic evaluation
of medical queue length, response times, and resource utilization.
"""

# Queue risk threshold counts (first aid queue)
QUEUE_LOW_THRESHOLD = 5
QUEUE_HIGH_THRESHOLD = 15

# Response time thresholds in minutes (medical dispatch)
RESPONSE_TIME_LOW_THRESHOLD = 3
RESPONSE_TIME_HIGH_THRESHOLD = 8

# Resource utilization thresholds in percent (Ambulance and Medical Staff)
UTILIZATION_MEDIUM_THRESHOLD = 50.0
UTILIZATION_HIGH_THRESHOLD = 80.0

# Total expected fields in MedicalInput (used for confidence scoring)
TOTAL_MEDICAL_TELEMETRY_FIELDS = 9
