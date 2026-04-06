"""Switch platform for Smart Irrigation."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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
    """Set up switch platform."""
    coordinator: SmartIrrigationCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for zone in coordinator.zones:
        entities.append(ZoneEnableSwitch(coordinator, zone))

    async_add_entities(entities)


class ZoneEnableSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to enable/disable a zone."""

    _attr_icon = "mdi:water-check"

    def __init__(
        self,
        coordinator: SmartIrrigationCoordinator,
        zone: IrrigationZone,
    ) -> None:
        """Initialize switch."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{DOMAIN}_{zone.zone_id}_enabled"
        self._attr_name = f"Bewässerung {zone.name} Aktiv"

    @property
    def is_on(self) -> bool:
        """Return if zone is enabled."""
        return self._zone.enabled

    async def async_turn_on(self, **kwargs) -> None:
        """Enable zone."""
        self._zone.enabled = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable zone."""
        self._zone.enabled = False
        self.async_write_ha_state()
