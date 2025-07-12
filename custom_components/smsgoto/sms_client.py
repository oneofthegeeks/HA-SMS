"""SMS GoTo Client using the GoTo Authentication package."""
import asyncio
import logging
import re
from typing import Optional

import aiohttp

# Import the GoTo Authentication package
try:
    from gotoconnect_auth import GoToConnectAuth
except ImportError:
    _LOGGER = logging.getLogger(__name__)
    _LOGGER.error("GoTo Authentication package not found. Please install it with: pip install gotoconnect-auth")
    GoToConnectAuth = None

_LOGGER = logging.getLogger(__name__)

# GoTo SMS API endpoint
GOTO_SMS_URL = "https://api.goto.com/rest/sms/v1/messages"


class SMSGoToClient:
    """Client for sending SMS messages via GoTo using the authentication package."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        account_sid: str,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """Initialize the SMS GoTo client."""
        if GoToConnectAuth is None:
            raise ImportError("GoTo Authentication package is required. Install with: pip install gotoconnect-auth")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.account_sid = account_sid
        self._session = session
        self._auth_client = None

    async def _get_auth_client(self) -> GoToConnectAuth:
        """Get or create the GoTo authentication client."""
        if self._auth_client is None:
            # Initialize the GoTo authentication client
            self._auth_client = GoToConnectAuth(
                client_id=self.api_key,
                client_secret=self.api_secret,
                redirect_uri="http://localhost:8080/callback"  # Not used for client credentials
            )
            
            # Authenticate using client credentials
            try:
                await self._auth_client.authenticate()
            except Exception as ex:
                _LOGGER.error("Failed to authenticate with GoTo: %s", ex)
                raise
        
        return self._auth_client

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
        """Test the connection to GoTo API using the authentication package."""
        try:
            auth_client = await self._get_auth_client()
            
            # Test by making a simple API call
            response = await auth_client.get("https://api.goto.com/rest/users/v1/users/me")
            
            if response.status_code == 200:
                _LOGGER.info("Successfully authenticated with GoTo API")
                return True
            else:
                _LOGGER.error("Authentication test failed: %s", response.status_code)
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
        """Send SMS message via GoTo using the authentication package."""
        try:
            # Validate phone number
            validated_to = self._validate_phone_number(to_number)
            
            # Get authenticated client
            auth_client = await self._get_auth_client()
            
            # Prepare SMS data
            sms_data = {
                "to": validated_to,
                "message": message,
                "account_sid": self.account_sid,
            }
            
            if from_number:
                validated_from = self._validate_phone_number(from_number)
                sms_data["from"] = validated_from
            
            # Send SMS using the authenticated client
            response = await auth_client.post(
                GOTO_SMS_URL,
                json=sms_data
            )
            
            if response.status_code == 200:
                result = response.json()
                _LOGGER.info("SMS sent successfully: %s", result)
                return True
            else:
                error_text = response.text
                _LOGGER.error("SMS send failed: %s - %s", response.status_code, error_text)
                return False
                    
        except Exception as ex:
            _LOGGER.error("Failed to send SMS: %s", ex)
            return False

    async def close(self):
        """Close the client session."""
        if self._auth_client:
            try:
                await self._auth_client.logout()
            except Exception as ex:
                _LOGGER.warning("Error during logout: %s", ex)
        
        if self._session and not self._session.closed:
            await self._session.close() 