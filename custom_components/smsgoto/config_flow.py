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
from .sms_client import SMSGoToClient, EmbeddedGoToAuth

_LOGGER = logging.getLogger(__name__)


class SMSGoToConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMS GoTo."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        super().__init__()
        self.auth_client = None
        self.auth_code = None

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Store the credentials
                self.api_key = user_input[CONF_API_KEY]
                self.api_secret = user_input[CONF_API_SECRET]
                self.account_sid = user_input[CONF_ACCOUNT_SID]
                self.integration_name = user_input.get(CONF_NAME, "SMS GoTo")

                # Create auth client and get authorization URL
                self.auth_client = EmbeddedGoToAuth(
                    client_id=self.api_key,
                    client_secret=self.api_secret,
                )

                # Check if we have saved tokens
                if self.auth_client.load_tokens():
                    if await self.auth_client._ensure_valid_token():
                        # We have valid tokens, proceed to test connection
                        return await self.async_step_test_connection()
                
                # No valid tokens, show OAuth URL
                auth_url = self.auth_client.get_authorization_url()
                return self.async_show_form(
                    step_id="oauth_setup",
                    data_schema=vol.Schema({
                        vol.Required("auth_code", description=f"1. Visit this URL in your browser:\n{auth_url}\n\n2. Complete the authorization\n\n3. Copy the authorization code from the redirect URL\n\n4. Paste the authorization code here:"): str,
                    }),
                    errors=errors,
                    description="Complete the OAuth flow to authenticate with GoTo",
                )

            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default="SMS GoTo"): str,
                    vol.Required(CONF_API_KEY, description="Your GoTo API Key (Client ID)"): str,
                    vol.Required(CONF_API_SECRET, description="Your GoTo API Secret (Client Secret)"): str,
                    vol.Required(CONF_ACCOUNT_SID, description="Your GoTo Account SID (Optional)"): str,
                }
            ),
            errors=errors,
            description="Enter your GoTo API credentials. You'll be guided through the OAuth setup process.",
        )

    async def async_step_oauth_setup(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the OAuth setup step."""
        errors = {}

        if user_input is not None:
            try:
                auth_code = user_input["auth_code"].strip()
                
                # Exchange authorization code for tokens
                if await self.auth_client.exchange_code_for_token(auth_code):
                    # Save tokens
                    if self.auth_client.save_tokens():
                        _LOGGER.info("OAuth flow completed successfully")
                        return await self.async_step_test_connection()
                    else:
                        errors["base"] = "token_save_failed"
                else:
                    errors["base"] = "oauth_failed"

            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.exception("OAuth setup error")
                errors["base"] = "oauth_failed"

        # Re-show the form with errors
        auth_url = self.auth_client.get_authorization_url()
        return self.async_show_form(
            step_id="oauth_setup",
            data_schema=vol.Schema({
                vol.Required("auth_code", description=f"1. Visit this URL in your browser:\n{auth_url}\n\n2. Complete the authorization\n\n3. Copy the authorization code from the redirect URL\n\n4. Paste the authorization code here:"): str,
            }),
            errors=errors,
            description="Complete the OAuth flow to authenticate with GoTo",
        )

    async def async_step_test_connection(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Test the connection with GoTo API."""
        errors = {}

        try:
            # Test the connection
            client = SMSGoToClient(
                api_key=self.api_key,
                api_secret=self.api_secret,
                account_sid=self.account_sid,
            )
            
            if await client.test_connection():
                return self.async_create_entry(
                    title=self.integration_name,
                    data={
                        CONF_NAME: self.integration_name,
                        CONF_API_KEY: self.api_key,
                        CONF_API_SECRET: self.api_secret,
                        CONF_ACCOUNT_SID: self.account_sid,
                    },
                )
            else:
                errors["base"] = "cannot_connect"
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.exception("Connection test error")
            errors["base"] = "unknown"

        if errors:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default=self.integration_name): str,
                        vol.Required(CONF_API_KEY, default=self.api_key): str,
                        vol.Required(CONF_API_SECRET, default=self.api_secret): str,
                        vol.Required(CONF_ACCOUNT_SID, default=self.account_sid): str,
                    }
                ),
                errors=errors,
                description="Connection test failed. Please check your credentials and try again.",
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