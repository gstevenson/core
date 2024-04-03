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


class PlaceholderHub:
    """Class to verify correct integration configuration."""

    def __init__(self) -> None:
        """Initialize."""

    async def validateinput(self, data: dict[str, Any]) -> bool:
        """Validate the user input has the mandatory values."""

        # Get the API key and airport ICAO code from the user input
        api_key = data[CONF_API_KEY]
        airport_icao_code = data["airport_icao_code"]

        # Check if API key and airport ICAO code are provided (HA should prevent this from happening anyway)
        if api_key is None and airport_icao_code is None:
            return False

        # Check API key is in correct format
        if len(api_key) != 32:
            return False

        # Check airport ICAO code is correct length
        if len(airport_icao_code) != 4:
            return False

        # Check the airport ICAO code is 4 letters only with no other characters
        if not airport_icao_code.isalpha():
            return False

        return True

    async def authenticate(self, api_key: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect to the METAR-TAF API.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    hub = PlaceholderHub()

    if not await hub.validateinput(data):
        raise InvalidAuth

    if not await hub.authenticate(data[CONF_API_KEY]):
        raise InvalidAuth

    # api_key = data[CONF_API_KEY]
    airport_icao_code = data["airport_icao_code"]

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

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
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
