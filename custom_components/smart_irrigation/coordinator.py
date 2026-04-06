"""Coordinator for Smart Irrigation."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_ZONES,
    CONF_ZONE_NAME,
    CONF_SWITCH_ENTITY,
    CONF_MOISTURE_ENTITY,
    CONF_WEATHER_ENTITY,
    CONF_MOISTURE_THRESHOLD_LOW,
    CONF_MOISTURE_THRESHOLD_HIGH,
    CONF_DURATION_MINUTES,
    CONF_SCHEDULE_START,
    CONF_SCHEDULE_END,
    CONF_RAIN_THRESHOLD_MM,
    CONF_ENABLED,
    DEFAULT_MOISTURE_LOW,
    DEFAULT_MOISTURE_HIGH,
    DEFAULT_DURATION,
    DEFAULT_SCHEDULE_START,
    DEFAULT_SCHEDULE_END,
    DEFAULT_RAIN_THRESHOLD,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class IrrigationZone:
    """Represents a single irrigation zone."""

    def __init__(self, zone_config: dict[str, Any]) -> None:
        """Initialize zone."""
        self.name: str = zone_config[CONF_ZONE_NAME]
        self.switch_entity: str = zone_config[CONF_SWITCH_ENTITY]
        self.moisture_entity: str | None = zone_config.get(CONF_MOISTURE_ENTITY)
        self.weather_entity: str | None = zone_config.get(CONF_WEATHER_ENTITY)
        self.moisture_low: float = zone_config.get(
            CONF_MOISTURE_THRESHOLD_LOW, DEFAULT_MOISTURE_LOW
        )
        self.moisture_high: float = zone_config.get(
            CONF_MOISTURE_THRESHOLD_HIGH, DEFAULT_MOISTURE_HIGH
        )
        self.duration: int = zone_config.get(CONF_DURATION_MINUTES, DEFAULT_DURATION)
        self.schedule_start: str = zone_config.get(
            CONF_SCHEDULE_START, DEFAULT_SCHEDULE_START
        )
        self.schedule_end: str = zone_config.get(
            CONF_SCHEDULE_END, DEFAULT_SCHEDULE_END
        )
        self.rain_threshold: float = zone_config.get(
            CONF_RAIN_THRESHOLD_MM, DEFAULT_RAIN_THRESHOLD
        )
        self.enabled: bool = zone_config.get(CONF_ENABLED, True)

        # Runtime state
        self.is_watering: bool = False
        self.last_watered: datetime | None = None
        self.next_watering: datetime | None = None
        self.current_moisture: float | None = None
        self.rain_expected: bool = False
        self.rain_amount_mm: float = 0.0
        self.skip_next: bool = False
        self.watering_reason: str | None = None
        self.skip_reason: str | None = None

    @property
    def zone_id(self) -> str:
        """Generate unique zone ID."""
        return self.name.lower().replace(" ", "_")


class SmartIrrigationCoordinator(DataUpdateCoordinator):
    """Coordinator that manages all irrigation zones."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL),
        )
        self.zones: list[IrrigationZone] = []
        self._config = config
        self._stop_timers: dict[str, Any] = {}

        # Build zones from config
        for zone_config in config.get(CONF_ZONES, []):
            self.zones.append(IrrigationZone(zone_config))

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data and evaluate watering logic."""
        zone_data = {}

        for zone in self.zones:
            await self._update_zone_state(zone)
            await self._evaluate_zone(zone)
            zone_data[zone.zone_id] = {
                "name": zone.name,
                "enabled": zone.enabled,
                "is_watering": zone.is_watering,
                "moisture": zone.current_moisture,
                "rain_expected": zone.rain_expected,
                "rain_amount_mm": zone.rain_amount_mm,
                "last_watered": zone.last_watered,
                "next_watering": zone.next_watering,
                "watering_reason": zone.watering_reason,
                "skip_reason": zone.skip_reason,
            }

        return zone_data

    async def _update_zone_state(self, zone: IrrigationZone) -> None:
        """Read current sensor states for a zone."""
        # Read moisture sensor
        if zone.moisture_entity:
            state = self.hass.states.get(zone.moisture_entity)
            if state and state.state not in ("unknown", "unavailable"):
                try:
                    zone.current_moisture = float(state.state)
                except ValueError:
                    _LOGGER.warning(
                        "Cannot parse moisture value '%s' for zone %s",
                        state.state,
                        zone.name,
                    )

        # Read switch state
        switch_state = self.hass.states.get(zone.switch_entity)
        if switch_state:
            zone.is_watering = switch_state.state == "on"

        # Read weather forecast
        if zone.weather_entity:
            await self._update_weather_forecast(zone)

    async def _update_weather_forecast(self, zone: IrrigationZone) -> None:
        """Check weather forecast for rain prediction."""
        weather_state = self.hass.states.get(zone.weather_entity)
        if not weather_state:
            return

        zone.rain_expected = False
        zone.rain_amount_mm = 0.0

        # Try to get forecast via weather service
        try:
            forecast_data = await self.hass.services.async_call(
                "weather",
                "get_forecasts",
                {"entity_id": zone.weather_entity, "type": "hourly"},
                blocking=True,
                return_response=True,
            )

            if not forecast_data:
                return

            forecasts = forecast_data.get(zone.weather_entity, {}).get("forecast", [])

            # Check next 24 hours for rain
            now = dt_util.now()
            cutoff = now + timedelta(hours=24)
            total_rain = 0.0

            for fc in forecasts:
                fc_time = dt_util.parse_datetime(fc.get("datetime", ""))
                if fc_time and fc_time <= cutoff:
                    precipitation = fc.get("precipitation", 0) or 0
                    total_rain += float(precipitation)

            zone.rain_amount_mm = round(total_rain, 1)
            zone.rain_expected = total_rain >= zone.rain_threshold

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.debug(
                "Could not get weather forecast for zone %s: %s", zone.name, err
            )

    async def _evaluate_zone(self, zone: IrrigationZone) -> None:
        """Decide whether a zone should water now."""
        zone.watering_reason = None
        zone.skip_reason = None

        if not zone.enabled:
            zone.skip_reason = "Zone deaktiviert"
            return

        if zone.skip_next:
            zone.skip_reason = "Manuell übersprungen"
            return

        if zone.is_watering:
            # Already watering, don't interfere
            return

        now = dt_util.now()

        # Check if we're in the schedule window
        if not self._is_in_schedule(zone, now):
            zone.skip_reason = "Außerhalb Zeitfenster"
            return

        # Check rain forecast
        if zone.rain_expected:
            zone.skip_reason = (
                f"Regen erwartet ({zone.rain_amount_mm}mm in 24h)"
            )
            return

        # Check moisture level
        needs_water = False
        if zone.current_moisture is not None:
            if zone.current_moisture < zone.moisture_low:
                needs_water = True
                zone.watering_reason = (
                    f"Bodenfeuchtigkeit niedrig ({zone.current_moisture}% < {zone.moisture_low}%)"
                )
        else:
            # No moisture sensor - water based on schedule only
            needs_water = True
            zone.watering_reason = "Zeitplan (kein Feuchtigkeitssensor)"

        # Already watered recently?
        if zone.last_watered:
            min_interval = timedelta(hours=4)
            if now - zone.last_watered < min_interval:
                zone.skip_reason = "Kürzlich bewässert"
                return

        if needs_water:
            await self._start_watering(zone)

    def _is_in_schedule(self, zone: IrrigationZone, now: datetime) -> bool:
        """Check if current time is within zone schedule."""
        try:
            start_parts = zone.schedule_start.split(":")
            end_parts = zone.schedule_end.split(":")
            start_time = now.replace(
                hour=int(start_parts[0]),
                minute=int(start_parts[1]),
                second=0,
                microsecond=0,
            )
            end_time = now.replace(
                hour=int(end_parts[0]),
                minute=int(end_parts[1]),
                second=0,
                microsecond=0,
            )
            return start_time <= now <= end_time
        except (ValueError, IndexError):
            _LOGGER.error("Invalid schedule for zone %s", zone.name)
            return False

    async def _start_watering(self, zone: IrrigationZone) -> None:
        """Start watering a zone."""
        _LOGGER.info(
            "Starting watering for zone %s (reason: %s)",
            zone.name,
            zone.watering_reason,
        )

        try:
            await self.hass.services.async_call(
                "switch",
                "turn_on",
                {"entity_id": zone.switch_entity},
                blocking=True,
            )
            zone.is_watering = True
            zone.last_watered = dt_util.now()

            # Schedule auto-stop
            stop_time = timedelta(minutes=zone.duration)

            @callback
            def _stop_watering(_now):
                """Stop watering after duration."""
                self.hass.async_create_task(self._stop_watering(zone))

            self._stop_timers[zone.zone_id] = async_track_time_interval(
                self.hass, _stop_watering, stop_time
            )

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Failed to start watering zone %s: %s", zone.name, err)

    async def _stop_watering(self, zone: IrrigationZone) -> None:
        """Stop watering a zone."""
        _LOGGER.info("Stopping watering for zone %s", zone.name)

        try:
            await self.hass.services.async_call(
                "switch",
                "turn_off",
                {"entity_id": zone.switch_entity},
                blocking=True,
            )
            zone.is_watering = False

            # Cancel timer
            if zone.zone_id in self._stop_timers:
                self._stop_timers[zone.zone_id]()
                del self._stop_timers[zone.zone_id]

            # Reset skip flag after watering
            zone.skip_next = False

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Failed to stop watering zone %s: %s", zone.name, err)

    async def manual_water(self, zone_id: str, duration: int | None = None) -> None:
        """Manually start watering a zone."""
        for zone in self.zones:
            if zone.zone_id == zone_id:
                if duration:
                    zone.duration = duration
                zone.watering_reason = "Manuell gestartet"
                await self._start_watering(zone)
                break

    async def skip_next_watering(self, zone_id: str) -> None:
        """Skip the next scheduled watering for a zone."""
        for zone in self.zones:
            if zone.zone_id == zone_id:
                zone.skip_next = True
                _LOGGER.info("Skipping next watering for zone %s", zone.name)
                break

    async def force_check(self) -> None:
        """Force an immediate check of all zones."""
        await self.async_refresh()
