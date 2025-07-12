"""OAuth Helper for SMS GoTo Integration."""

import asyncio
import logging
from .sms_client import EmbeddedGoToAuth

_LOGGER = logging.getLogger(__name__)


async def complete_oauth_flow(client_id: str, client_secret: str) -> bool:
    """Complete the OAuth flow and save tokens."""
    auth_client = EmbeddedGoToAuth(client_id, client_secret)
    
    # Get the authorization URL
    auth_url = auth_client.get_authorization_url()
    print(f"\n=== GoTo OAuth Setup ===")
    print(f"1. Visit this URL in your browser:")
    print(f"   {auth_url}")
    print(f"\n2. Complete the authorization in your browser")
    print(f"3. You'll be redirected to a URL like:")
    print(f"   http://localhost:8123/auth/external/callback?code=AUTHORIZATION_CODE&state=homeassistant_sms_goto")
    print(f"\n4. Copy the authorization code from the URL")
    
    # Get the authorization code from user
    auth_code = input("\nEnter the authorization code: ").strip()
    
    if not auth_code:
        print("No authorization code provided")
        return False
    
    # Exchange code for tokens
    if await auth_client.exchange_code_for_token(auth_code):
        # Save tokens
        if auth_client.save_tokens():
            print("✅ OAuth flow completed successfully!")
            print("✅ Tokens saved and will be automatically refreshed")
            return True
        else:
            print("❌ Failed to save tokens")
            return False
    else:
        print("❌ Failed to exchange authorization code for tokens")
        return False


def get_auth_url(client_id: str) -> str:
    """Get the authorization URL for manual setup."""
    auth_client = EmbeddedGoToAuth(client_id, "dummy_secret")
    return auth_client.get_authorization_url()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python oauth_helper.py <client_id> <client_secret>")
        sys.exit(1)
    
    client_id = sys.argv[1]
    client_secret = sys.argv[2]
    
    asyncio.run(complete_oauth_flow(client_id, client_secret)) 