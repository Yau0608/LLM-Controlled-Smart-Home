# Mobile Interface for Smart Home Voice Control

This component adds a web-based interface that allows you to control your smart home using voice commands from your mobile phone or any web browser.

## How It Works

The mobile interface runs a web server on your desktop computer that:

1. Hosts a simple web page with a "Hold to Speak" button
2. Captures audio from your phone's microphone
3. Sends it to your desktop for processing
4. Returns the text and audio response to your phone

All the heavy processing (Whisper transcription, LLM processing, and TTS generation) happens on your desktop computer, making this solution very lightweight for the phone.

## Setup and Usage

### 1. Install Requirements

Make sure you have Flask installed:
```bash
pip install flask
```
Or update all requirements:
```bash
pip install -r requirements.txt
```

### 2. Start the Server

Run the mobile interface server:
```bash
cd main/core
python run_mobile.py
```

The server will display a URL like `http://192.168.x.x:5000` - this is the address you'll access from your phone.

### 3. Connect from Your Phone

1. Make sure your phone is connected to the same WiFi network as your desktop
2. Open a web browser on your phone
3. Enter the URL shown when you started the server
4. Allow microphone access when prompted
5. Press and hold the green button to speak, release to send

### 4. Using the Interface

- **Hold to Speak**: Press and hold the button while speaking your command
- **Release to Send**: The command will be processed when you release the button
- **Text Response**: The text response will appear below the button
- **Voice Response**: You'll hear the voice response through your phone's speakers

## Troubleshooting

- **Can't Connect**: Make sure your phone and desktop are on the same WiFi network
- **Microphone Access**: Check that you've allowed microphone access in your browser settings
- **Audio Issues**: Some browsers have better audio support than others (Chrome often works best)
- **Connection Problems**: If your connection is slow, try reducing the quality of the audio or moving closer to your WiFi router 