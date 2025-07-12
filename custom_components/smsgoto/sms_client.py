"""SMS GoTo Client with simple API authentication."""
import logging
import re
from typing import Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)

# GoTo API endpoints
GOTO_SMS_URL = "https://api.goto.com/rest/sms/v1/messages"
GOTO_USER_INFO_URL = "https://api.goto.com/rest/users/v1/users/me"


class SMSGoToClient:
    """Client for sending SMS messages via GoTo with simple API authentication."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        account_sid: str,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """Initialize the SMS GoTo client."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.account_sid = account_sid
        self._session = session

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _validate_phone_number(self, phone_number: str) -> str:
        """Validate and format phone number."""
        # Remove all non-digit characters
        cleaned = re.sub(r'[^\d]', '', phone_number)
        
        # Ensure it starts with country code
        if len(cleaned) == 10:
            cleaned = "1" + cleaned  # Assume US number
        elif len(cleaned) == 11 and cleaned.startswith("1"):
            pass  # Already has US country code
        elif len(cleaned) < 10:
            raise ValueError("Phone number too short")
        elif len(cleaned) > 15:
            raise ValueError("Phone number too long")
        
        return cleaned

    async def test_connection(self) -> bool:
        """Test the connection to GoTo API."""
        try:
            _LOGGER.debug("Testing connection to GoTo API")
            session = await self._get_session()
            
            # Use basic auth with API key and secret
            auth = aiohttp.BasicAuth(self.api_key, self.api_secret)
            
            # Test by making a simple API call to get user info
            async with session.get(GOTO_USER_INFO_URL, auth=auth) as response:
                if response.status == 200:
                    user_data = await response.json()
                    _LOGGER.info("Successfully authenticated with GoTo API. User: %s", user_data.get("email", "Unknown"))
                    return True
                else:
                    error_text = await response.text()
                    _LOGGER.error("Authentication test failed: %s - %s", response.status, error_text)
                    return False
                    
        except Exception as ex:
            _LOGGER.error("Connection test failed: %s", ex)
            return False

    async def send_sms(
        self,
        to_number: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> bool:
        """Send SMS message via GoTo."""
        try:
            # Validate phone number
            validated_to = self._validate_phone_number(to_number)
            
            session = await self._get_session()
            auth = aiohttp.BasicAuth(self.api_key, self.api_secret)
            
            # Prepare SMS data
            sms_data = {
                "to": validated_to,
                "message": message,
            }
            
            if from_number:
                sms_data["from"] = from_number
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            _LOGGER.debug("Sending SMS to %s: %s", validated_to, message)
            
            async with session.post(
                GOTO_SMS_URL, 
                json=sms_data, 
                auth=auth, 
                headers=headers
            ) as response:
                if response.status == 200 or response.status == 201:
                    result = await response.json()
                    _LOGGER.info("SMS sent successfully to %s", validated_to)
                    return True
                else:
                    error_text = await response.text()
                    _LOGGER.error("Failed to send SMS: %s - %s", response.status, error_text)
                    return False
                    
        except Exception as ex:
            _LOGGER.error("SMS send error: %s", ex)
            return False

    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close() 