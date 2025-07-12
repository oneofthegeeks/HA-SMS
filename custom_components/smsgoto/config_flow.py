"""Config flow for SMS GoTo integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_API_KEY, CONF_API_SECRET, CONF_ACCOUNT_SID, DOMAIN
from .sms_client import SMSGoToClient

_LOGGER = logging.getLogger(__name__)


class SMSGoToConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMS GoTo."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Test the connection
                client = SMSGoToClient(
                    api_key=user_input[CONF_API_KEY],
                    api_secret=user_input[CONF_API_SECRET],
                    account_sid=user_input[CONF_ACCOUNT_SID],
                )
                
                if await client.test_connection():
                    return self.async_create_entry(
                        title=user_input.get(CONF_NAME, "SMS GoTo"),
                        data=user_input,
                    )
                else:
                    errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default="SMS GoTo"): str,
                    vol.Required(CONF_API_KEY, description="Your GoTo API Key (Client ID)"): str,
                    vol.Required(CONF_API_SECRET, description="Your GoTo API Secret (Client Secret)"): str,
                    vol.Required(CONF_ACCOUNT_SID, description="Your GoTo Account SID"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/oneofthegeeks/GoTo-Authentication",
                "setup_url": "https://github.com/oneofthegeeks/HA-SMS"
            },
        )

    async def async_step_import(self, import_info: Dict[str, Any]) -> FlowResult:
        """Set up this integration using yaml."""
        return await self.async_step_user(import_info)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class MissingDependency(HomeAssistantError):
    """Error to indicate missing dependency.""" 