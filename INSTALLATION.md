# SMS GoTo Home Assistant Integration - Installation Guide

## Prerequisites

1. **Home Assistant Installation**: You need a working Home Assistant installation (version 2023.8 or later)
2. **GoTo Account**: You need a GoTo account with SMS capabilities and API access
3. **GoTo API Credentials**: You'll need your API Key, API Secret, and Account SID
4. **GoTo Authentication Package**: The integration requires the [GoTo Authentication library](https://github.com/oneofthegeeks/GoTo-Authentication)

## Installation Methods

### Method 1: Manual Installation (Recommended for testing)

1. **Download the Integration**:
   - Download this repository or copy the files to your local machine
   - Ensure you have the complete `custom_components/sms_goto/` directory structure

2. **Copy to Home Assistant**:
   - Copy the `custom_components/sms_goto/` folder to your Home Assistant `config/custom_components/` directory
   - The final path should be: `config/custom_components/sms_goto/`

3. **Install GoTo Authentication Package**:
   ```bash
   pip install gotoconnect-auth
   ```

4. **Restart Home Assistant**:
   - Go to **Settings** > **System** > **Restart**
   - Click **Restart** to reload the configuration

5. **Install Dependencies**:
   - The integration requires `aiohttp>=3.8.0` and `gotoconnect-auth>=1.0.0`
   - These should be automatically installed by Home Assistant
   - If you encounter issues, you may need to install them manually in your Home Assistant environment

### Method 2: HACS Installation

1. **Install HACS** (if not already installed):
   - Follow the [HACS installation guide](https://hacs.xyz/docs/installation/manual)
   - Restart Home Assistant after installing HACS

2. **Add Custom Repository**:
   - Go to **HACS** > **Integrations**
   - Click the three dots in the top right corner
   - Select **Custom repositories**
   - Add this repository URL
   - Set category to **Integration**

3. **Install the Integration**:
   - Search for "SMS GoTo" in HACS
   - Click **Download**
   - Install the GoTo Authentication package:
     ```bash
     pip install gotoconnect-auth
     ```
   - Restart Home Assistant

## Configuration

### Step 1: Get Your GoTo Credentials

1. **Log into your GoTo account**
2. **Navigate to API settings** (usually under Developer or API section)
3. **Note down your credentials**:
   - API Key (Client ID)
   - API Secret (Client Secret)
   - Account SID

### Step 2: Configure in Home Assistant

1. **Open Home Assistant**
2. **Go to Settings** > **Devices & Services** > **Integrations**
3. **Click "Add Integration"**
4. **Search for "SMS GoTo"**
5. **Enter your credentials**:
   - **Integration Name**: Choose a friendly name (e.g., "SMS GoTo")
   - **API Key**: Your GoTo API key (Client ID)
   - **API Secret**: Your GoTo API secret (Client Secret)
   - **Account SID**: Your GoTo account SID
6. **Click "Submit"**

The integration will test the connection using the GoTo Authentication package and create the configuration if successful.

### Step 3: Test the Integration

1. **Go to Developer Tools** > **Services**
2. **Select the service**: `sms_goto.send_sms`
3. **Enter test data**:
   ```yaml
   to: "+1234567890"
   message: "Test SMS from Home Assistant!"
   ```
4. **Click "Call Service"**

You should receive an SMS if everything is configured correctly.

## Troubleshooting

### Common Issues

#### 1. "Integration not found"
- **Solution**: Ensure the `custom_components/sms_goto/` folder is in the correct location
- **Check**: The path should be `config/custom_components/sms_goto/`
- **Restart**: Restart Home Assistant after copying files

#### 2. "GoTo Authentication package not found"
- **Solution**: Install the GoTo Authentication package
- **Command**: `pip install gotoconnect-auth`
- **Restart**: Restart Home Assistant after installation

#### 3. "Failed to connect to GoTo API"
- **Check**: Verify your API credentials are correct
- **Verify**: Ensure your GoTo account has SMS capabilities
- **Test**: Use the test script to verify credentials outside of Home Assistant

#### 4. "Module not found" errors
- **Solution**: Install the required dependencies
- **Command**: `pip install aiohttp>=3.8.0 gotoconnect-auth>=1.0.0` in your Home Assistant environment

#### 5. "Invalid phone number format"
- **Solution**: Ensure phone numbers include country code
- **Format**: Use `+1234567890` format
- **Test**: Try different phone number formats

### Testing Outside Home Assistant

Use the provided test script to verify your credentials:

```bash
python test_sms_goto.py YOUR_API_KEY YOUR_API_SECRET YOUR_ACCOUNT_SID YOUR_PHONE_NUMBER
```

### Debug Logging

Enable debug logging to troubleshoot issues:

```yaml
logger:
  custom_components.sms_goto: debug
```

Add this to your `configuration.yaml` file and restart Home Assistant.

## Next Steps

After successful installation:

1. **Create Automations**: Use the SMS service in your automations
2. **Set up Notifications**: Configure the notify platform
3. **Test Scenarios**: Create test automations to verify functionality
4. **Monitor Logs**: Check logs for any issues

## Support

If you encounter issues:

1. **Check the logs** for detailed error messages
2. **Verify your credentials** using the test script
3. **Check the Home Assistant Community** for similar issues
4. **Open an issue** on the GitHub repository

## Files Structure

After installation, your directory structure should look like:

```
config/
├── custom_components/
│   └── sms_goto/
│       ├── __init__.py
│       ├── const.py
│       ├── config_flow.py
│       ├── notify.py
│       ├── sms_client.py
│       ├── manifest.json
│       ├── services.yaml
│       └── translations/
│           └── en.json
└── configuration.yaml
```

## Dependencies

The integration requires the following Python packages:
- `aiohttp>=3.8.0` - For HTTP requests
- `gotoconnect-auth>=1.0.0` - GoTo Authentication library

These will be automatically installed by Home Assistant, but you may need to install them manually if you encounter issues. 