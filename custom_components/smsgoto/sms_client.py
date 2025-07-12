"""SMS GoTo Client with embedded GoTo Authentication."""
import asyncio
import logging
import re
import time
from typing import Optional, Dict, Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

# GoTo SMS API endpoint
GOTO_SMS_URL = "https://api.goto.com/rest/sms/v1/messages"
GOTO_TOKEN_URL = "https://authentication.logmeininc.com/oauth/token"


class EmbeddedGoToAuth:
    """Embedded GoTo Authentication client."""
    
    def __init__(self, client_id: str, client_secret: str):
        """Initialize the embedded auth client."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = 0
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def authenticate(self) -> bool:
        """Authenticate with GoTo using client credentials."""
        try:
            session = await self._get_session()
            
            # Prepare authentication data
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            
            # Get access token
            async with session.post(GOTO_TOKEN_URL, data=auth_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = time.time() + expires_in - 300  # 5 min buffer
                    
                    _LOGGER.info("Successfully authenticated with GoTo")
                    return True
                else:
                    error_text = await response.text()
                    _LOGGER.error("Authentication failed: %s - %s", response.status, error_text)
                    return False
                    
        except Exception as ex:
            _LOGGER.error("Authentication error: %s", ex)
            return False
    
    async def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token."""
        if not self.access_token or time.time() >= self.token_expires_at:
            return await self.authenticate()
        return True
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated GET request."""
        if not await self._ensure_valid_token():
            raise Exception("Failed to authenticate")
        
        session = await self._get_session()
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        kwargs["headers"] = headers
        
        return await session.get(url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated POST request."""
        if not await self._ensure_valid_token():
            raise Exception("Failed to authenticate")
        
        session = await self._get_session()
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        kwargs["headers"] = headers
        
        return await session.post(url, **kwargs)
    
    async def logout(self):
        """Logout and cleanup."""
        if self._session and not self._session.closed:
            await self._session.close()


class SMSGoToClient:
    """Client for sending SMS messages via GoTo with embedded authentication."""

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
        self._auth_client = None

    async def _get_auth_client(self) -> EmbeddedGoToAuth:
        """Get or create the embedded authentication client."""
        if self._auth_client is None:
            self._auth_client = EmbeddedGoToAuth(
                client_id=self.api_key,
                client_secret=self.api_secret,
            )
            
            # Authenticate
            if not await self._auth_client.authenticate():
                raise Exception("Failed to authenticate with GoTo")
        
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
        """Test the connection to GoTo API."""
        try:
            auth_client = await self._get_auth_client()
            
            # Test by making a simple API call
            response = await auth_client.get("https://api.goto.com/rest/users/v1/users/me")
            
            if response.status == 200:
                _LOGGER.info("Successfully authenticated with GoTo API")
                return True
            else:
                _LOGGER.error("Authentication test failed: %s", response.status)
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
            
            if response.status == 200:
                result = await response.json()
                _LOGGER.info("SMS sent successfully: %s", result)
                return True
            else:
                error_text = await response.text()
                _LOGGER.error("SMS send failed: %s - %s", response.status, error_text)
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