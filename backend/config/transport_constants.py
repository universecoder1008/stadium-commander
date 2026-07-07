"""Constants for the transport analyzer and simulator.

Contains threshold limits and baseline variables used for deterministic evaluation
of parking occupancy, transit delays, and spectator travel predictions.
"""

# Parking occupancy threshold percentages
PARKING_MEDIUM_THRESHOLD = 70.0
PARKING_HIGH_THRESHOLD = 90.0

# Transit delay thresholds in minutes (Metro and Bus)
DELAY_MEDIUM_THRESHOLD = 5
DELAY_HIGH_THRESHOLD = 15

# Baseline travel/transit time in minutes for spectators to arrive at stadium
BASE_TRANSIT_TIME = 15

# Total number of expected fields in TransportInput (used for confidence scoring)
TOTAL_TELEMETRY_FIELDS = 9
