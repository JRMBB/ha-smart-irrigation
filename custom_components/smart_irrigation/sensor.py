"""Sensor platform for Smart Irrigation."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartIrrigationCoordinator, IrrigationZone


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator: SmartIrrigationCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for zone in coordinator.zones:
        entities.append(ZoneMoistureSensor(coordinator, zone))
        entities.append(ZoneStatusSensor(coordinator, zone))
        entities.append(ZoneRainForecastSensor(coordinator, zone))

    async_add_entities(entities)


class ZoneMoistureSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing current moisture level for a zone."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(
        self,
        coordinator: SmartIrrigationCoordinator,
        zone: IrrigationZone,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{DOMAIN}_{zone.zone_id}_moisture"
        self._attr_name = f"Bewässerung {zone.name} Feuchtigkeit"

    @property
    def native_value(self) -> float | None:
        """Return moisture level."""
        data = self.coordinator.data
        if data and self._zone.zone_id in data:
            return data[self._zone.zone_id].get("moisture")
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        return {
            "threshold_low": self._zone.moisture_low,
            "threshold_high": self._zone.moisture_high,
            "zone": self._zone.name,
        }


class ZoneStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing current status/decision for a zone."""

    _attr_icon = "mdi:sprinkler-variant"

    def __init__(
        self,
        coordinator: SmartIrrigationCoordinator,
        zone: IrrigationZone,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{DOMAIN}_{zone.zone_id}_status"
        self._attr_name = f"Bewässerung {zone.name} Status"

    @property
    def native_value(self) -> str:
        """Return zone status."""
        data = self.coordinator.data
        if data and self._zone.zone_id in data:
            zone_data = data[self._zone.zone_id]
            if zone_data.get("is_watering"):
                return "Bewässert"
            if not zone_data.get("enabled"):
                return "Deaktiviert"
            if zone_data.get("skip_reason"):
                return f"Pause: {zone_data['skip_reason']}"
            return "Bereit"
        return "Unbekannt"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        data = self.coordinator.data
        attrs = {"zone": self._zone.name}
        if data and self._zone.zone_id in data:
            zone_data = data[self._zone.zone_id]
            attrs["last_watered"] = zone_data.get("last_watered")
            attrs["watering_reason"] = zone_data.get("watering_reason")
            attrs["skip_reason"] = zone_data.get("skip_reason")
            attrs["schedule"] = (
                f"{self._zone.schedule_start} - {self._zone.schedule_end}"
            )
            attrs["duration_minutes"] = self._zone.duration
        return attrs

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        data = self.coordinator.data
        if data and self._zone.zone_id in data:
            if data[self._zone.zone_id].get("is_watering"):
                return "mdi:sprinkler"
            if data[self._zone.zone_id].get("rain_expected"):
                return "mdi:weather-rainy"
        return "mdi:sprinkler-variant"


class ZoneRainForecastSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing expected rain amount."""

    _attr_icon = "mdi:weather-pouring"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "mm"

    def __init__(
        self,
        coordinator: SmartIrrigationCoordinator,
        zone: IrrigationZone,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{DOMAIN}_{zone.zone_id}_rain"
        self._attr_name = f"Bewässerung {zone.name} Regenvorhersage"

    @property
    def native_value(self) -> float | None:
        """Return expected rain amount."""
        data = self.coordinator.data
        if data and self._zone.zone_id in data:
            return data[self._zone.zone_id].get("rain_amount_mm", 0)
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        data = self.coordinator.data
        attrs = {"zone": self._zone.name}
        if data and self._zone.zone_id in data:
            attrs["rain_expected"] = data[self._zone.zone_id].get("rain_expected")
            attrs["threshold_mm"] = self._zone.rain_threshold
        return attrs
