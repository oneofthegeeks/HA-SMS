"""SMS GoTo Client with embedded GoTo Authentication."""
import asyncio
import logging
import re
import time
import json
from typing import Optional, Dict, Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

# GoTo API endpoints
GOTO_SMS_URL = "https://api.goto.com/rest/sms/v1/messages"
GOTO_TOKEN_URL = "https://authentication.logmeininc.com/oauth/token"
GOTO_AUTH_URL = "https://authentication.logmeininc.com/oauth/authorize"
GOTO_USER_INFO_URL = "https://api.goto.com/rest/users/v1/users/me"


class EmbeddedGoToAuth:
    """Embedded GoTo Authentication client with OAuth2 flow and token refresh."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8123/auth/external/callback"):
        """Initialize the embedded auth client."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = 0
        self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    def get_authorization_url(self) -> str:
        """Get the authorization URL for OAuth2 flow."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "SMS",  # Adjust scope as needed
            "state": "homeassistant_sms_goto"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{GOTO_AUTH_URL}?{query_string}"
    
    async def exchange_code_for_token(self, authorization_code: str) -> bool:
        """Exchange authorization code for access token and refresh token."""
        try:
            session = await self._get_session()
            
            token_data = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": authorization_code,
                "redirect_uri": self.redirect_uri,
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            _LOGGER.debug("Exchanging authorization code for token")
            
            async with session.post(GOTO_TOKEN_URL, data=token_data, headers=headers) as response:
                if response.status == 200:
                    token_response = await response.json()
                    self.access_token = token_response.get("access_token")
                    self.refresh_token = token_response.get("refresh_token")
                    expires_in = token_response.get("expires_in", 3600)
                    self.token_expires_at = time.time() + expires_in - 300  # 5 min buffer
                    
                    _LOGGER.info("Successfully obtained access token and refresh token")
                    return True
                else:
                    error_text = await response.text()
                    _LOGGER.error("Token exchange failed: %s - %s", response.status, error_text)
                    return False
                    
        except Exception as ex:
            _LOGGER.error("Token exchange error: %s", ex)
            return False
    
    async def refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            _LOGGER.error("No refresh token available")
            return False
            
        try:
            session = await self._get_session()
            
            refresh_data = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            _LOGGER.debug("Refreshing access token")
            
            async with session.post(GOTO_TOKEN_URL, data=refresh_data, headers=headers) as response:
                if response.status == 200:
                    token_response = await response.json()
                    self.access_token = token_response.get("access_token")
                    
                    # Update refresh token if a new one is provided
                    new_refresh_token = token_response.get("refresh_token")
                    if new_refresh_token:
                        self.refresh_token = new_refresh_token
                    
                    expires_in = token_response.get("expires_in", 3600)
                    self.token_expires_at = time.time() + expires_in - 300
                    
                    _LOGGER.info("Successfully refreshed access token")
                    return True
                else:
                    error_text = await response.text()
                    _LOGGER.error("Token refresh failed: %s - %s", response.status, error_text)
                    return False
                    
        except Exception as ex:
            _LOGGER.error("Token refresh error: %s", ex)
            return False
    
    async def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token, refreshing if necessary."""
        if not self.access_token:
            _LOGGER.warning("No access token available. Please complete OAuth flow first.")
            return False
            
        if time.time() >= self.token_expires_at:
            _LOGGER.debug("Token expired, attempting refresh")
            return await self.refresh_access_token()
            
        return True
    
    def save_tokens(self, file_path: str = "/config/smsgoto_tokens.json") -> bool:
        """Save tokens to file for persistence."""
        try:
            token_data = {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expires_at": self.token_expires_at,
                "client_id": self.client_id
            }
            
            with open(file_path, 'w') as f:
                json.dump(token_data, f)
            
            _LOGGER.debug("Tokens saved to %s", file_path)
            return True
        except Exception as ex:
            _LOGGER.error("Failed to save tokens: %s", ex)
            return False
    
    def load_tokens(self, file_path: str = "/config/smsgoto_tokens.json") -> bool:
        """Load tokens from file."""
        try:
            with open(file_path, 'r') as f:
                token_data = json.load(f)
            
            # Only load if client_id matches
            if token_data.get("client_id") == self.client_id:
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                self.token_expires_at = token_data.get("expires_at", 0)
                
                _LOGGER.debug("Tokens loaded from %s", file_path)
                return True
            else:
                _LOGGER.warning("Client ID mismatch, not loading tokens")
                return False
                
        except FileNotFoundError:
            _LOGGER.debug("No saved tokens found")
            return False
        except Exception as ex:
            _LOGGER.error("Failed to load tokens: %s", ex)
            return False
    
    async def authenticate(self) -> bool:
        """Try to authenticate using saved tokens or prompt for OAuth flow."""
        # First try to load saved tokens
        if self.load_tokens():
            if await self._ensure_valid_token():
                _LOGGER.info("Successfully authenticated using saved tokens")
                return True
        
        # If no valid tokens, need to complete OAuth flow
        auth_url = self.get_authorization_url()
        _LOGGER.warning("No valid tokens found. Please complete OAuth flow:")
        _LOGGER.warning("1. Visit this URL in your browser: %s", auth_url)
        _LOGGER.warning("2. Complete the authorization")
        _LOGGER.warning("3. Copy the authorization code from the redirect URL")
        _LOGGER.warning("4. Call exchange_code_for_token() with the code")
        
        return False
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated GET request."""
        if not await self._ensure_valid_token():
            raise Exception("Failed to authenticate")
        
        session = await self._get_session()
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers["Accept"] = "application/json"
        kwargs["headers"] = headers
        
        return await session.get(url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated POST request."""
        if not await self._ensure_valid_token():
            raise Exception("Failed to authenticate")
        
        session = await self._get_session()
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
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
            _LOGGER.debug("Creating new authentication client")
            self._auth_client = EmbeddedGoToAuth(
                client_id=self.api_key,
                client_secret=self.api_secret,
            )
            
            # Try to authenticate
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
            _LOGGER.debug("Testing connection to GoTo API")
            auth_client = await self._get_auth_client()
            
            # Test by making a simple API call to get user info
            response = await auth_client.get(GOTO_USER_INFO_URL)
            
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
            
            # Get authenticated client
            auth_client = await self._get_auth_client()
            
            # Prepare SMS data
            sms_data = {
                "to": validated_to,
                "message": message,
            }
            
            # Add account_sid if provided
            if self.account_sid:
                sms_data["account_sid"] = self.account_sid
            
            # Add from_number if provided
            if from_number:
                validated_from = self._validate_phone_number(from_number)
                sms_data["from"] = validated_from
            
            _LOGGER.debug("Sending SMS with data: %s", sms_data)
            
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