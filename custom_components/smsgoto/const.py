"""Constants for the SMS GoTo integration."""

DOMAIN = "smsgoto"

# Configuration keys
CONF_API_KEY = "api_key"
CONF_API_SECRET = "api_secret"
CONF_ACCOUNT_SID = "account_sid"

# Service names
SERVICE_SEND_SMS = "send_sms"

# Platforms
PLATFORMS = ["notify"]

# Default values
DEFAULT_NAME = "SMS GoTo"

# Error messages
ERROR_INVALID_PHONE = "Invalid phone number format"
ERROR_SMS_FAILED = "Failed to send SMS"
ERROR_INVALID_CREDENTIALS = "Invalid API credentials" 