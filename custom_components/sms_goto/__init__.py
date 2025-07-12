"""SMS GoTo Integration for Home Assistant."""
import asyncio
import logging
import subprocess
import sys
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_ACCOUNT_SID,
    DOMAIN,
    PLATFORMS,
    SERVICE_SEND_SMS,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Required(CONF_API_SECRET): cv.string,
                vol.Required(CONF_ACCOUNT_SID): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_SEND_SMS_SCHEMA = vol.Schema(
    {
        vol.Required("to"): cv.string,
        vol.Required("message"): cv.string,
        vol.Optional("from_number"): cv.string,
    }
)


def install_goto_auth():
    """Install the GoTo Authentication package from GitHub if not available."""
    try:
        import gotoconnect_auth
        return True
    except ImportError:
        _LOGGER.info("GoTo Authentication package not found. Installing from GitHub...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "git+https://github.com/oneofthegeeks/GoTo-Authentication.git"
            ])
            _LOGGER.info("GoTo Authentication package installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            _LOGGER.error("Failed to install GoTo Authentication package: %s", e)
            return False


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the SMS GoTo component."""
    if DOMAIN not in config:
        return True

    # Install GoTo Authentication package if needed
    if not install_goto_auth():
        _LOGGER.error("Failed to install required dependencies")
        return False

    hass.data.setdefault(DOMAIN, {})

    # Import SMS client after ensuring dependencies are installed
    from .sms_client import SMSGoToClient

    # Create client
    client = SMSGoToClient(
        api_key=config[DOMAIN][CONF_API_KEY],
        api_secret=config[DOMAIN][CONF_API_SECRET],
        account_sid=config[DOMAIN][CONF_ACCOUNT_SID],
    )

    # Test connection
    try:
        await client.test_connection()
    except Exception as ex:
        _LOGGER.error("Failed to connect to SMS service: %s", ex)
        raise ConfigEntryNotReady from ex

    hass.data[DOMAIN]["client"] = client

    # Register service
    async def async_send_sms(call: ServiceCall) -> None:
        """Send SMS message."""
        to_number = call.data["to"]
        message = call.data["message"]
        from_number = call.data.get("from_number")

        try:
            await client.send_sms(
                to_number=to_number,
                message=message,
                from_number=from_number,
            )
            _LOGGER.info("SMS sent successfully to %s", to_number)
        except Exception as ex:
            _LOGGER.error("Failed to send SMS: %s", ex)

    hass.services.async_register(
        DOMAIN, SERVICE_SEND_SMS, async_send_sms, schema=SERVICE_SEND_SMS_SCHEMA
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SMS GoTo from a config entry."""
    # Install GoTo Authentication package if needed
    if not install_goto_auth():
        _LOGGER.error("Failed to install required dependencies")
        return False

    hass.data.setdefault(DOMAIN, {})

    # Import SMS client after ensuring dependencies are installed
    from .sms_client import SMSGoToClient

    # Create client
    client = SMSGoToClient(
        api_key=entry.data[CONF_API_KEY],
        api_secret=entry.data[CONF_API_SECRET],
        account_sid=entry.data[CONF_ACCOUNT_SID],
    )

    # Test connection
    try:
        await client.test_connection()
    except Exception as ex:
        _LOGGER.error("Failed to connect to SMS service: %s", ex)
        raise ConfigEntryNotReady from ex

    hass.data[DOMAIN]["client"] = client

    # Register service
    async def async_send_sms(call: ServiceCall) -> None:
        """Send SMS message."""
        to_number = call.data["to"]
        message = call.data["message"]
        from_number = call.data.get("from_number")

        try:
            await client.send_sms(
                to_number=to_number,
                message=message,
                from_number=from_number,
            )
            _LOGGER.info("SMS sent successfully to %s", to_number)
        except Exception as ex:
            _LOGGER.error("Failed to send SMS: %s", ex)

    hass.services.async_register(
        DOMAIN, SERVICE_SEND_SMS, async_send_sms, schema=SERVICE_SEND_SMS_SCHEMA
    )

    # Set up platforms
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop("client", None)

    return unload_ok 