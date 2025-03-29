import requests
import json
import os
import time
import pygame
from io import BytesIO
import urllib.parse

# Configuration
API_URL = "http://192.168.0.212:9880"  # Updated to your specific IP
SAVE_DIR = os.path.join(os.path.dirname(__file__), "temp")
DEBUG = True

# Reference audio configuration
DEFAULT_REF_AUDIO = "C:\\Users\\Yau\\Documents\\YauProject\\GPT-SoVITS-v3lora-20250228\\test\\A1 (Neutral).wav"
DEFAULT_PROMPT = "But I commissioned it long before, like... I commissioned it a long time before we released it. So like, I was right in the middle of my voice lessons."
DEFAULT_PROMPT_LANG = "en"
DEFAULT_TEXT_LANG = "en"

# Create save directory if it doesn't exist
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Initialize pygame for audio playback
pygame.mixer.init()

def log(message):
    """Print debug messages"""
    if DEBUG:
        print(f"DEBUG: {message}")

def play_audio(audio_data):
    """Play audio data using pygame"""
    try:
        # Create a BytesIO object from the audio data
        audio_io = BytesIO(audio_data)
        
        # Load and play the audio
        pygame.mixer.music.load(audio_io)
        pygame.mixer.music.play()
        
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        print("Finished playing audio")
        
    except Exception as e:
        print(f"Error playing audio: {e}")

def test_tts_api(text, ref_audio_path=None, prompt_text=None, prompt_lang=None, text_lang=None):
    """Test the GPT-SoVITS API with a simple text request"""
    try:
        print(f"Testing TTS API with text: '{text}'")
        
        # Use default values if not provided
        ref_audio_path = ref_audio_path or DEFAULT_REF_AUDIO
        prompt_text = prompt_text or DEFAULT_PROMPT
        prompt_lang = prompt_lang or DEFAULT_PROMPT_LANG
        text_lang = text_lang or DEFAULT_TEXT_LANG
        
        # Construct the URL with query parameters
        params = {
            "refer_wav_path": ref_audio_path,
            "prompt_text": prompt_text,
            "prompt_language": prompt_lang,
            "text": text,
            "text_language": text_lang,
            "top_k": 15,
            "top_p": 1,
            "temperature": 1,
            "speed": 1
        }
        
        # Construct the full URL
        url = f"{API_URL}/?" + urllib.parse.urlencode(params)
        log(f"Sending request to: {url}")
        
        # Send the GET request
        response = requests.get(url)
        
        # Check response status
        if response.status_code != 200:
            print(f"Error from API: {response.status_code} - {response.text}")
            return False
        
        print(f"Response received! Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        
        # Handle audio response
        audio_data = response.content
        
        # Save the audio file
        audio_file = os.path.join(SAVE_DIR, f"test_tts_{int(time.time())}.wav")
        with open(audio_file, "wb") as f:
            f.write(audio_data)
        
        print(f"Audio saved to: {audio_file}")
        
        # Play the audio
        print("Playing audio...")
        play_audio(audio_data)
        
        return True
                
    except Exception as e:
        print(f"Error testing TTS API: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test GPT-SoVITS API")
    parser.add_argument("--ref", "--reference", dest="reference", 
                      help=f"Path to reference audio file (.wav) [default: {DEFAULT_REF_AUDIO}]")
    parser.add_argument("--prompt", dest="prompt", 
                      help=f"Text content of the reference audio [default: {DEFAULT_PROMPT[:30]}...]")
    parser.add_argument("--prompt-lang", dest="prompt_lang", default=DEFAULT_PROMPT_LANG,
                      help=f"Language of the prompt text (en, zh, ja, etc.) [default: {DEFAULT_PROMPT_LANG}]")
    parser.add_argument("--text-lang", dest="text_lang", default=DEFAULT_TEXT_LANG,
                      help=f"Language of the output text (en, zh, ja, etc.) [default: {DEFAULT_TEXT_LANG}]")
    parser.add_argument("--text", dest="text", 
                      help="Text to convert to speech (will override test messages)")
    args = parser.parse_args()
    
    # Test messages
    messages = [
        "Hello, I am your smart home assistant. I can control your lights and TV.",
        "I've turned the lights on at 75% brightness.",
        "The current temperature is 72 degrees Fahrenheit."
    ]
    
    # Run the test with the provided text or first test message
    print("\n===== TESTING GPT-SOVITS API =====")
    print(f"API URL: {API_URL}")
    
    test_text = args.text if args.text else messages[0]
    
    success = test_tts_api(
        test_text,
        ref_audio_path=args.reference,
        prompt_text=args.prompt,
        prompt_lang=args.prompt_lang,
        text_lang=args.text_lang
    )
    
    if success:
        print("\nAPI TEST SUCCESSFUL! 🎉")
        
        # Only ask about test messages if we didn't provide a custom text
        if not args.text:
            # Ask if user wants to test more messages
            response = input("\nDo you want to test more messages? (y/n): ")
            if response.lower() == 'y':
                for i, msg in enumerate(messages[1:], 1):
                    print(f"\n----- Testing message {i+1} -----")
                    test_tts_api(
                        msg,
                        ref_audio_path=args.reference,
                        prompt_text=args.prompt,
                        prompt_lang=args.prompt_lang,
                        text_lang=args.text_lang
                    )
    else:
        print("\nAPI TEST FAILED! 😞")
        print("\nPossible issues:")
        print("1. GPT-SoVITS API is not running at the specified URL")
        print("2. The reference audio file path is incorrect or inaccessible")
        print("3. Parameters may need adjustment")
        print("\nPlease check the API documentation and make sure the service is running.") 