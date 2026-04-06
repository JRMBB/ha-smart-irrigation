"""Config flow for Smart Irrigation."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

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
    DEFAULT_MOISTURE_LOW,
    DEFAULT_MOISTURE_HIGH,
    DEFAULT_DURATION,
    DEFAULT_SCHEDULE_START,
    DEFAULT_SCHEDULE_END,
    DEFAULT_RAIN_THRESHOLD,
)

_LOGGER = logging.getLogger(__name__)


class SmartIrrigationConfigFlow(
    config_entries.ConfigFlow, domain=DOMAIN
):
    """Handle a config flow for Smart Irrigation."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._zones: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step - add first zone."""
        if user_input is not None:
            self._zones.append(user_input)
            return await self.async_step_add_more()

        return self.async_show_form(
            step_id="user",
            data_schema=self._zone_schema(),
            description_placeholders={"zone_number": "1"},
        )

    async def async_step_add_more(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Ask if user wants to add more zones."""
        if user_input is not None:
            if user_input.get("add_another"):
                return await self.async_step_additional_zone()

            # Done adding zones - create entry
            return self.async_create_entry(
                title="Smart Irrigation",
                data={CONF_ZONES: self._zones},
            )

        return self.async_show_form(
            step_id="add_more",
            data_schema=vol.Schema(
                {
                    vol.Required("add_another", default=False): bool,
                }
            ),
            description_placeholders={
                "zone_count": str(len(self._zones)),
            },
        )

    async def async_step_additional_zone(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle adding another zone."""
        if user_input is not None:
            self._zones.append(user_input)
            return await self.async_step_add_more()

        return self.async_show_form(
            step_id="additional_zone",
            data_schema=self._zone_schema(),
            description_placeholders={
                "zone_number": str(len(self._zones) + 1),
            },
        )

    def _zone_schema(self) -> vol.Schema:
        """Return schema for a zone."""
        return vol.Schema(
            {
                vol.Required(CONF_ZONE_NAME): str,
                vol.Required(CONF_SWITCH_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="switch"),
                ),
                vol.Optional(CONF_MOISTURE_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor"),
                ),
                vol.Optional(CONF_WEATHER_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="weather"),
                ),
                vol.Optional(
                    CONF_MOISTURE_THRESHOLD_LOW, default=DEFAULT_MOISTURE_LOW
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=100, step=1, unit_of_measurement="%"
                    ),
                ),
                vol.Optional(
                    CONF_MOISTURE_THRESHOLD_HIGH, default=DEFAULT_MOISTURE_HIGH
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=100, step=1, unit_of_measurement="%"
                    ),
                ),
                vol.Optional(
                    CONF_DURATION_MINUTES, default=DEFAULT_DURATION
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=120, step=1, unit_of_measurement="min"
                    ),
                ),
                vol.Optional(
                    CONF_SCHEDULE_START, default=DEFAULT_SCHEDULE_START
                ): selector.TimeSelector(),
                vol.Optional(
                    CONF_SCHEDULE_END, default=DEFAULT_SCHEDULE_END
                ): selector.TimeSelector(),
                vol.Optional(
                    CONF_RAIN_THRESHOLD_MM, default=DEFAULT_RAIN_THRESHOLD
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0, max=50, step=0.5, unit_of_measurement="mm"
                    ),
                ),
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SmartIrrigationOptionsFlow:
        """Get the options flow."""
        return SmartIrrigationOptionsFlow(config_entry)


class SmartIrrigationOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Smart Irrigation."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage options - select zone to edit."""
        zones = self._config_entry.data.get(CONF_ZONES, [])
        zone_names = {
            str(i): z[CONF_ZONE_NAME] for i, z in enumerate(zones)
        }
        zone_names["new"] = "➕ Neue Zone hinzufügen"

        if user_input is not None:
            selected = user_input.get("zone_select")
            if selected == "new":
                return await self.async_step_add_zone()
            # Edit existing zone
            self._editing_index = int(selected)
            return await self.async_step_edit_zone()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("zone_select"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(value=k, label=v)
                                for k, v in zone_names.items()
                            ],
                            mode=selector.SelectSelectorMode.LIST,
                        ),
                    ),
                }
            ),
        )

    async def async_step_edit_zone(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Edit an existing zone."""
        zones = list(self._config_entry.data.get(CONF_ZONES, []))
        zone = zones[self._editing_index]

        if user_input is not None:
            zones[self._editing_index] = user_input
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data={**self._config_entry.data, CONF_ZONES: zones},
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="edit_zone",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ZONE_NAME, default=zone.get(CONF_ZONE_NAME, "")
                    ): str,
                    vol.Required(
                        CONF_SWITCH_ENTITY,
                        default=zone.get(CONF_SWITCH_ENTITY, ""),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="switch"),
                    ),
                    vol.Optional(
                        CONF_MOISTURE_ENTITY,
                        description={"suggested_value": zone.get(CONF_MOISTURE_ENTITY)},
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor"),
                    ),
                    vol.Optional(
                        CONF_WEATHER_ENTITY,
                        description={"suggested_value": zone.get(CONF_WEATHER_ENTITY)},
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="weather"),
                    ),
                    vol.Optional(
                        CONF_MOISTURE_THRESHOLD_LOW,
                        default=zone.get(CONF_MOISTURE_THRESHOLD_LOW, DEFAULT_MOISTURE_LOW),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=100, step=1, unit_of_measurement="%"
                        ),
                    ),
                    vol.Optional(
                        CONF_MOISTURE_THRESHOLD_HIGH,
                        default=zone.get(CONF_MOISTURE_THRESHOLD_HIGH, DEFAULT_MOISTURE_HIGH),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=100, step=1, unit_of_measurement="%"
                        ),
                    ),
                    vol.Optional(
                        CONF_DURATION_MINUTES,
                        default=zone.get(CONF_DURATION_MINUTES, DEFAULT_DURATION),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=120, step=1, unit_of_measurement="min"
                        ),
                    ),
                    vol.Optional(
                        CONF_SCHEDULE_START,
                        default=zone.get(CONF_SCHEDULE_START, DEFAULT_SCHEDULE_START),
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_SCHEDULE_END,
                        default=zone.get(CONF_SCHEDULE_END, DEFAULT_SCHEDULE_END),
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_RAIN_THRESHOLD_MM,
                        default=zone.get(CONF_RAIN_THRESHOLD_MM, DEFAULT_RAIN_THRESHOLD),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=50, step=0.5, unit_of_measurement="mm"
                        ),
                    ),
                }
            ),
        )

    async def async_step_add_zone(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Add a new zone via options."""
        if user_input is not None:
            zones = list(self._config_entry.data.get(CONF_ZONES, []))
            zones.append(user_input)
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data={**self._config_entry.data, CONF_ZONES: zones},
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="add_zone",
            data_schema=SmartIrrigationConfigFlow._zone_schema(None),
        )
