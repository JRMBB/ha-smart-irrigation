"""Constants for Smart Irrigation."""

DOMAIN = "smart_irrigation"
PLATFORMS = ["sensor", "switch", "binary_sensor"]

# Config keys
CONF_ZONES = "zones"
CONF_ZONE_NAME = "zone_name"
CONF_SWITCH_ENTITY = "switch_entity"
CONF_MOISTURE_ENTITY = "moisture_entity"
CONF_WEATHER_ENTITY = "weather_entity"
CONF_MOISTURE_THRESHOLD_LOW = "moisture_threshold_low"
CONF_MOISTURE_THRESHOLD_HIGH = "moisture_threshold_high"
CONF_DURATION_MINUTES = "duration_minutes"
CONF_SCHEDULE_START = "schedule_start"
CONF_SCHEDULE_END = "schedule_end"
CONF_RAIN_THRESHOLD_MM = "rain_threshold_mm"
CONF_ENABLED = "enabled"

# Defaults
DEFAULT_MOISTURE_LOW = 30
DEFAULT_MOISTURE_HIGH = 60
DEFAULT_DURATION = 15
DEFAULT_SCHEDULE_START = "06:00"
DEFAULT_SCHEDULE_END = "08:00"
DEFAULT_RAIN_THRESHOLD = 2.0

# Attributes
ATTR_ZONE_NAME = "zone_name"
ATTR_LAST_WATERED = "last_watered"
ATTR_NEXT_WATERING = "next_watering"
ATTR_MOISTURE_LEVEL = "moisture_level"
ATTR_RAIN_EXPECTED = "rain_expected"
ATTR_RAIN_AMOUNT = "rain_amount_mm"
ATTR_WATERING_REASON = "watering_reason"
ATTR_SKIP_REASON = "skip_reason"

# Services
SERVICE_MANUAL_WATER = "manual_water"
SERVICE_SKIP_NEXT = "skip_next"
SERVICE_FORCE_CHECK = "force_check"

# Update interval in minutes
UPDATE_INTERVAL = 5
