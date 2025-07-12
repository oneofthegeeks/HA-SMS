# SMS GoTo Home Assistant Integration

This custom integration for Home Assistant allows you to send SMS messages using the [GoTo Authentication API](https://github.com/oneofthegeeks/GoTo-Authentication). It provides both a service for sending SMS messages and a notify platform for integration with Home Assistant's notification system.

## Features

- Send SMS messages via GoTo API using the official authentication package
- Integration with Home Assistant's notification system
- Configurable via Home Assistant UI
- Phone number validation and formatting
- Automatic token refresh using the GoTo Authentication library
- Error handling and logging

## Prerequisites

- **GoTo Authentication Package**: This integration uses the [GoTo Authentication library](https://github.com/oneofthegeeks/GoTo-Authentication) (installed automatically from GitHub)
- **GoTo Account**: You need a GoTo account with SMS capabilities and API access
- **GoTo API Credentials**: You'll need your API Key, API Secret, and Account SID

## Installation

### Method 1: Manual Installation

1. Download this repository
2. Copy the `custom_components/sms_goto` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant (the GoTo Authentication package will be installed automatically)
4. Go to **Settings** > **Devices & Services** > **Integrations**
5. Click **Add Integration** and search for "SMS GoTo"
6. Follow the configuration steps

### Method 2: HACS Installation (Recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Add this repository as a custom repository in HACS
3. Install the integration through HACS
4. Restart Home Assistant (the GoTo Authentication package will be installed automatically)
5. Configure the integration through the UI

## Configuration

### Required Credentials

You'll need the following credentials from your GoTo account:

- **API Key**: Your GoTo API key (Client ID)
- **API Secret**: Your GoTo API secret (Client Secret)
- **Account SID**: Your GoTo account SID

### Configuration Steps

1. Go to **Settings** > **Devices & Services** > **Integrations**
2. Click **Add Integration**
3. Search for "SMS GoTo"
4. Enter your credentials:
   - **Integration Name**: A friendly name for the integration
   - **API Key**: Your GoTo API key (Client ID)
   - **API Secret**: Your GoTo API secret (Client Secret)
   - **Account SID**: Your GoTo account SID
5. Click **Submit**

The integration will test the connection using the GoTo Authentication package and create the configuration if successful.

## Usage

### Service Call

You can send SMS messages using the `sms_goto.send_sms` service:

```yaml
service: sms_goto.send_sms
data:
  to: "+1234567890"
  message: "Hello from Home Assistant!"
  from_number: "+1987654321"  # Optional
```

### Notify Platform

The integration also creates a notify platform that you can use in automations:

```yaml
automation:
  - alias: "Send SMS Alert"
    trigger:
      platform: state
      entity_id: sensor.motion_detector
      to: "on"
    action:
      service: notify.sms_goto
      data:
        target: "+1234567890"
        message: "Motion detected in your home!"
        data:
          from_number: "+1987654321"  # Optional
```

### Examples

#### Send SMS when door opens:

```yaml
automation:
  - alias: "Door Open SMS Alert"
    trigger:
      platform: state
      entity_id: binary_sensor.front_door
      to: "on"
    action:
      service: sms_goto.send_sms
      data:
        to: "+1234567890"
        message: "Front door has been opened!"
```

#### Send SMS with sensor data:

```yaml
automation:
  - alias: "Temperature Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.living_room_temperature
      above: 80
    action:
      service: sms_goto.send_sms
      data:
        to: "+1234567890"
        message: "Temperature alert: {{ states('sensor.living_room_temperature') }}°F in living room"
```

#### Send SMS at specific time:

```yaml
automation:
  - alias: "Daily Reminder"
    trigger:
      platform: time
      at: "08:00:00"
    action:
      service: sms_goto.send_sms
      data:
        to: "+1234567890"
        message: "Good morning! Don't forget to check your Home Assistant dashboard."
```

## Phone Number Format

The integration automatically formats phone numbers. You can use any of these formats:

- `+1234567890`
- `1234567890`
- `(123) 456-7890`
- `123-456-7890`

The integration will automatically:
- Remove all non-digit characters
- Add US country code (+1) if not present
- Validate the number length

## Troubleshooting

### Common Issues

1. **"GoTo Authentication package not found"**
   - The integration will automatically install it from GitHub
   - If it fails, you may need to install git on your system
   - Restart Home Assistant after installation

2. **"Failed to connect to GoTo API"**
   - Check your API credentials
   - Ensure your GoTo account has SMS capabilities
   - Verify your internet connection

3. **"Invalid phone number format"**
   - Ensure the phone number includes the country code
   - Check that the number is between 10-15 digits

4. **"SMS send failed"**
   - Check your GoTo account balance
   - Verify the destination number is valid
   - Check if your account has SMS permissions

### Logs

Check the Home Assistant logs for detailed error messages:

```yaml
logger:
  custom_components.sms_goto: debug
```

## Development

### Requirements

- Python 3.9+
- aiohttp>=3.8.0
- git+https://github.com/oneofthegeeks/GoTo-Authentication.git
- Home Assistant 2023.8+

### Testing

To test the integration locally:

1. Install the requirements
2. Set up your GoTo credentials
3. Run the integration tests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

1. Check the [Home Assistant Community](https://community.home-assistant.io/)
2. Open an issue on [GitHub](https://github.com/oneofthegeeks/HA-SMS)
3. Check the [GoTo Authentication Documentation](https://github.com/oneofthegeeks/GoTo-Authentication)

## Changelog

### Version 1.0.0
- Initial release
- SMS sending functionality using GoTo Authentication package from GitHub
- Notify platform integration
- Config flow support
- Phone number validation

## Author

Created by **Taylor Brinton** ([@oneofthegeeks](https://github.com/oneofthegeeks))

## Acknowledgments

- [GoTo Authentication](https://github.com/oneofthegeeks/GoTo-Authentication) for providing the authentication library
- Home Assistant community for the excellent platform 