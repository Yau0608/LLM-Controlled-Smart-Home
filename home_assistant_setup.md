# Home Assistant Configuration Guide

This guide will help you set up Home Assistant for use with the Voice Command System.

## Prerequisites

1. A running Home Assistant instance
   - [Install Home Assistant](https://www.home-assistant.io/installation/)
   - Recommended: Use Home Assistant OS on a Raspberry Pi or similar device

## Setting Up Home Assistant API Access

### 1. Create a Long-Lived Access Token

1. Log in to your Home Assistant instance
2. Click on your profile (bottom left corner)
3. Scroll down to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Give it a name like "Voice Command System"
6. Copy the token and keep it safe (you won't be able to see it again)

### 2. Configure the project to use your Home Assistant instance

Create a file named `config.json` in the `main/core` directory with the following content:

```json
{
  "homeassistant": {
    "url": "http://YOUR_HOME_ASSISTANT_IP:8123",
    "token": "YOUR_LONG_LIVED_ACCESS_TOKEN"
  }
}
```

Replace:
- `YOUR_HOME_ASSISTANT_IP` with your Home Assistant IP address
- `YOUR_LONG_LIVED_ACCESS_TOKEN` with the token you created earlier

## Testing the Connection

Once you've configured the system, you can test it by:

1. Ensuring Home Assistant is running
2. Starting the Voice Command System
3. Trying a simple light command like "Turn on the living room light"

## Supported Entities

The system currently supports controlling:
- Lights (on/off, brightness, color)

## Troubleshooting

- Make sure your Home Assistant instance is reachable from the machine running the Voice Command System
- Verify that the token has not expired
- Check that the URL format is correct (http or https depending on your setup)
- Ensure the entities you're trying to control actually exist in your Home Assistant setup

## Additional Resources

- [Home Assistant API Documentation](https://developers.home-assistant.io/docs/api/rest/)
- [Home Assistant Python Library Documentation](https://github.com/home-assistant/home-assistant-api) 