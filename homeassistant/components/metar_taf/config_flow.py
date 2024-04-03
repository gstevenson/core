"""Config flow for METAR-TAF integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Required("airport_icao_code"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect to the METAR-TAF API.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    # Get the API key and airport ICAO code from the user input
    api_key = data[CONF_API_KEY]
    airport_icao_code = data["airport_icao_code"]

    # Check if API key and airport ICAO code are provided (HA should prevent this from happening anyway so we don't bother raising a custom error here)
    if api_key is None and airport_icao_code is None:
        raise InvalidAuth

    # Check API key is in correct format
    if len(api_key) != 32:
        raise ApiKeyInvalidFormat

    # Check airport ICAO code is correct length
    if len(airport_icao_code) != 4:
        raise AirportIcaoCodeInvalid

    # Check the airport ICAO code is 4 letters only with no other characters
    if not airport_icao_code.isalpha():
        raise AirportIcaoCodeInvalid

    # Check the API token is actually valid
    # if 1 == 2:
    #    raise CannotConnect
    # if not await hub.authenticate(data[CONF_API_KEY]):
    #     raise InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": f"METAR-TAF ({airport_icao_code})"}


class MetarTafConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the METAR-TAF integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(f"{32323}_{5545}")
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except AirportIcaoCodeInvalid:
                errors["base"] = "airport_icao_code_invalid"
            except ApiKeyInvalidFormat:
                errors["base"] = "api_key_invalid_format"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # We reach this if we've passed all validation so now we need to create the device
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class AirportIcaoCodeInvalid(HomeAssistantError):
    """Error to indicate the airport ICAO code is invalid."""


class ApiKeyInvalidFormat(HomeAssistantError):
    """Error to indicate the API key is in the wrong format."""
