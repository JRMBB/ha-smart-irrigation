"""Smart Irrigation - Intelligente Bewässerungssteuerung für Home Assistant."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_MANUAL_WATER,
    SERVICE_SKIP_NEXT,
    SERVICE_FORCE_CHECK,
)
from .coordinator import SmartIrrigationCoordinator

_LOGGER = logging.getLogger(__name__)

MANUAL_WATER_SCHEMA = vol.Schema(
    {
        vol.Required("zone_id"): cv.string,
        vol.Optional("duration"): cv.positive_int,
    }
)

SKIP_NEXT_SCHEMA = vol.Schema(
    {
        vol.Required("zone_id"): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Irrigation from a config entry."""
    coordinator = SmartIrrigationCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_manual_water(call: ServiceCall) -> None:
        """Handle manual watering service."""
        zone_id = call.data["zone_id"]
        duration = call.data.get("duration")
        for coord in hass.data[DOMAIN].values():
            await coord.manual_water(zone_id, duration)

    async def handle_skip_next(call: ServiceCall) -> None:
        """Handle skip next watering service."""
        zone_id = call.data["zone_id"]
        for coord in hass.data[DOMAIN].values():
            await coord.skip_next_watering(zone_id)

    async def handle_force_check(call: ServiceCall) -> None:
        """Handle force check service."""
        for coord in hass.data[DOMAIN].values():
            await coord.force_check()

    hass.services.async_register(
        DOMAIN, SERVICE_MANUAL_WATER, handle_manual_water, schema=MANUAL_WATER_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SKIP_NEXT, handle_skip_next, schema=SKIP_NEXT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_FORCE_CHECK, handle_force_check
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # Remove services if no more entries
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_MANUAL_WATER)
            hass.services.async_remove(DOMAIN, SERVICE_SKIP_NEXT)
            hass.services.async_remove(DOMAIN, SERVICE_FORCE_CHECK)

    return unload_ok
