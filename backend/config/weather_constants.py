"""Constants for the weather analyzer and simulator.

Contains threshold limits and baseline variables used for deterministic evaluation
of rain, wind speed, visibility metrics, and weather-related operational impacts.
"""

# Rain probability thresholds in percent
RAIN_MEDIUM_THRESHOLD = 30.0
RAIN_HIGH_THRESHOLD = 70.0

# Wind speed thresholds in km/h
WIND_MEDIUM_THRESHOLD = 20.0
WIND_HIGH_THRESHOLD = 45.0

# Visibility thresholds in meters
VISIBILITY_HIGH_RISK_LIMIT = 1000.0  # Under 1000 meters is HIGH risk
VISIBILITY_MEDIUM_RISK_LIMIT = 5000.0  # Under 5000 meters is MEDIUM risk

# Operational delays in minutes per hazard type
LIGHTNING_DELAY_MINUTES = 45
RAIN_DELAY_MINUTES = 20
WIND_DELAY_MINUTES = 10
MEDIUM_DELAY_MINUTES = 5
LOW_DELAY_MINUTES = 0

# Total expected telemetry fields in WeatherInput
TOTAL_WEATHER_TELEMETRY_FIELDS = 6
