#!/usr/bin/env python3
"""
Test script for SMS GoTo integration.
This script can be used to test the SMS functionality outside of Home Assistant.
"""

import asyncio
import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

from sms_goto.sms_client import SMSGoToClient


async def test_sms_goto():
    """Test the SMS GoTo client functionality."""
    
    # Configuration - replace with your actual credentials
    API_KEY = "your_api_key_here"
    API_SECRET = "your_api_secret_here"
    ACCOUNT_SID = "your_account_sid_here"
    
    # Test phone number - replace with your actual phone number
    TEST_PHONE = "+1234567890"
    
    print("Testing SMS GoTo Integration")
    print("=" * 40)
    
    try:
        # Create client
        print("Creating SMS client...")
        client = SMSGoToClient(
            api_key=API_KEY,
            api_secret=API_SECRET,
            account_sid=ACCOUNT_SID,
        )
        
        # Test connection
        print("Testing connection...")
        if await client.test_connection():
            print("✓ Connection successful!")
        else:
            print("✗ Connection failed!")
            return
        
        # Test phone number validation
        print("\nTesting phone number validation...")
        test_numbers = [
            "+1234567890",
            "1234567890",
            "(123) 456-7890",
            "123-456-7890",
        ]
        
        for number in test_numbers:
            try:
                validated = client._validate_phone_number(number)
                print(f"✓ {number} -> {validated}")
            except ValueError as e:
                print(f"✗ {number} -> Error: {e}")
        
        # Test SMS sending (uncomment to actually send SMS)
        print("\nTesting SMS sending...")
        print("Note: Uncomment the following code to actually send an SMS")
        
        # Uncomment the following lines to test actual SMS sending:
        # success = await client.send_sms(
        #     to_number=TEST_PHONE,
        #     message="Test SMS from Home Assistant SMS GoTo integration!",
        # )
        # if success:
        #     print("✓ SMS sent successfully!")
        # else:
        #     print("✗ SMS sending failed!")
        
        # Close client
        await client.close()
        print("\n✓ Test completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Check if credentials are provided
    if len(sys.argv) > 3:
        # Usage: python test_sms_goto.py API_KEY API_SECRET ACCOUNT_SID [PHONE_NUMBER]
        api_key = sys.argv[1]
        api_secret = sys.argv[2]
        account_sid = sys.argv[3]
        test_phone = sys.argv[4] if len(sys.argv) > 4 else "+1234567890"
        
        # Update the test function to use provided credentials
        async def test_with_credentials():
            client = SMSGoToClient(
                api_key=api_key,
                api_secret=api_secret,
                account_sid=account_sid,
            )
            
            print("Testing SMS GoTo Integration")
            print("=" * 40)
            
            try:
                # Test connection
                print("Testing connection...")
                if await client.test_connection():
                    print("✓ Connection successful!")
                else:
                    print("✗ Connection failed!")
                    return False
                
                # Test SMS sending
                print(f"\nSending test SMS to {test_phone}...")
                success = await client.send_sms(
                    to_number=test_phone,
                    message="Test SMS from Home Assistant SMS GoTo integration!",
                )
                
                if success:
                    print("✓ SMS sent successfully!")
                else:
                    print("✗ SMS sending failed!")
                
                await client.close()
                return success
                
            except Exception as e:
                print(f"✗ Test failed with error: {e}")
                return False
        
        # Run the test
        result = asyncio.run(test_with_credentials())
        sys.exit(0 if result else 1)
    else:
        print("Usage: python test_sms_goto.py API_KEY API_SECRET ACCOUNT_SID [PHONE_NUMBER]")
        print("Or edit the script to add your credentials and run without arguments.")
        sys.exit(1) 