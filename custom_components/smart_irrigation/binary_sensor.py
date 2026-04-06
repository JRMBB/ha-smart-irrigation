"""Binary sensor platform for Smart Irrigation."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartIrrigationCoordinator, IrrigationZone


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor platform."""
    coordinator: SmartIrrigationCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for zone in coordinator.zones:
        entities.append(ZoneWateringBinarySensor(coordinator, zone))
        entities.append(ZoneRainExpectedBinarySensor(coordinator, zone))

    async_add_entities(entities)


class ZoneWateringBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor that indicates if a zone is currently watering."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_icon = "mdi:sprinkler"

    def __init__(
        self,
        coordinator: SmartIrrigationCoordinator,
        zone: IrrigationZone,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{DOMAIN}_{zone.zone_id}_watering"
        self._attr_name = f"Bewässerung {zone.name} Aktiv"

    @property
    def is_on(self) -> bool:
        """Return if zone is currently watering."""
        data = self.coordinator.data
        if data and self._zone.zone_id in data:
            return data[self._zone.zone_id].get("is_watering", False)
        return False


class ZoneRainExpectedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor that indicates if rain is expected."""

    _attr_device_class = BinarySensorDeviceClass.MOISTURE
    _attr_icon = "mdi:weather-rainy"

    def __init__(
        self,
        coordinator: SmartIrrigationCoordinator,
        zone: IrrigationZone,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{DOMAIN}_{zone.zone_id}_rain_expected"
        self._attr_name = f"Bewässerung {zone.name} Regen erwartet"

    @property
    def is_on(self) -> bool:
        """Return if rain is expected."""
        data = self.coordinator.data
        if data and self._zone.zone_id in data:
            return data[self._zone.zone_id].get("rain_expected", False)
        return False
