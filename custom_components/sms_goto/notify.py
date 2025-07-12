"""SMS GoTo Notify platform for Home Assistant."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    BaseNotificationService,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN
from .sms_client import SMSGoToClient

_LOGGER = logging.getLogger(__name__)


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> Optional[BaseNotificationService]:
    """Get the SMS GoTo notification service."""
    if discovery_info is None:
        return None

    client = hass.data[DOMAIN].get("client")
    if client is None:
        _LOGGER.error("SMS GoTo client not available")
        return None

    return SMSGoToNotificationService(client)


class SMSGoToNotificationService(BaseNotificationService):
    """SMS GoTo notification service."""

    def __init__(self, client: SMSGoToClient):
        """Initialize the notification service."""
        self.client = client

    async def async_send_message(self, message: str, **kwargs: Any) -> None:
        """Send SMS message."""
        targets = kwargs.get(ATTR_TARGET, [])
        data = kwargs.get(ATTR_DATA, {})
        
        # Get from_number from data or use default
        from_number = data.get("from_number")
        
        for target in targets:
            try:
                success = await self.client.send_sms(
                    to_number=target,
                    message=message,
                    from_number=from_number,
                )
                if success:
                    _LOGGER.info("SMS sent successfully to %s", target)
                else:
                    _LOGGER.error("Failed to send SMS to %s", target)
            except Exception as ex:
                _LOGGER.error("Error sending SMS to %s: %s", target, ex) 