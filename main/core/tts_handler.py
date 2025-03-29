import requests
import json
import os
import time
import pygame
import re
import glob
from io import BytesIO
import urllib.parse

# Hard-coded reference audio configuration
DEFAULT_REF_AUDIO = "C:\\Users\\Yau\\Documents\\YauProject\\GPT-SoVITS-v3lora-20250228\\test\\A1 (Neutral).wav"
DEFAULT_PROMPT_TEXT = "But I commissioned it long before, like... I commissioned it a long time before we released it. So like, I was right in the middle of my voice lessons."
DEFAULT_PROMPT_LANG = "en"
DEFAULT_API_URL = "http://127.0.0.212:9880"

class TTSHandler:
    """
    Text-to-Speech handler using GPT-SoVITS API
    
    This class manages text-to-speech conversion and playback using the GPT-SoVITS API.
    It sends text to the API, receives audio data, and plays it locally.
    """
    
    def __init__(self, api_url=DEFAULT_API_URL, debug_mode=False):
        """
        Initialize the TTS Handler
        
        Args:
            api_url (str): URL of the GPT-SoVITS API
            debug_mode (bool): Enable debug logging
        """
        self.api_url = api_url
        self.debug_mode = debug_mode
        self.audio_dir = os.path.join(os.path.dirname(__file__), "temp")
        self.latest_output_file = os.path.join(self.audio_dir, "latest_tts_output.wav")
        
        # Default reference audio configuration - use the hard-coded values
        self.default_ref_audio = DEFAULT_REF_AUDIO
        self.default_prompt_text = DEFAULT_PROMPT_TEXT
        self.default_prompt_lang = DEFAULT_PROMPT_LANG
        
        # Create the audio directory if it doesn't exist
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
        
        # Clean up old TTS output files
        self._cleanup_old_tts_files()
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        print(f"TTS Handler initialized with API URL: {api_url}")
        print(f"Using reference audio: {self.default_ref_audio}")
    
    def _cleanup_old_tts_files(self):
        """Clean up old TTS output files from previous runs"""
        try:
            # Find all tts_output_*.wav files
            old_files = glob.glob(os.path.join(self.audio_dir, "tts_output_*.wav"))
            
            # Delete them
            for file in old_files:
                try:
                    os.remove(file)
                    if self.debug_mode:
                        self.log(f"Deleted old TTS file: {file}")
                except Exception as e:
                    self.log(f"Could not delete file {file}: {e}")
        except Exception as e:
            self.log(f"Error cleaning up old TTS files: {e}")
    
    def log(self, message):
        """Print debug messages only if debug mode is enabled"""
        if self.debug_mode:
            print(f"TTS DEBUG: {message}")
    
    def set_default_reference(self, ref_audio_path, prompt_text, prompt_lang="en"):
        """
        Set default reference audio for TTS
        
        Args:
            ref_audio_path (str): Path to reference audio file
            prompt_text (str): Text content of the reference audio
            prompt_lang (str): Language of the reference audio
        """
        self.default_ref_audio = ref_audio_path
        self.default_prompt_text = prompt_text
        self.default_prompt_lang = prompt_lang
        self.log(f"Default reference set: {ref_audio_path}, '{prompt_text}' ({prompt_lang})")
    
    def clean_for_speech(self, text):
        """
        Clean the response text for speech synthesis by removing command patterns
        
        Args:
            text (str): The original response text
            
        Returns:
            str: Cleaned text suitable for speech synthesis
        """
        if not text:
            return ""
            
        # Store the original text for comparison
        original_text = text
        
        # Remove LIGHT commands with all parameters (handles multiple commands)
        text = re.sub(r'LIGHT:[\w]+:(ON|OFF)(:[\w]+=[\w\d,]+)*', '', text, flags=re.IGNORECASE)
        
        # Remove TV commands
        text = re.sub(r'TV:(ON|OFF)', '', text, flags=re.IGNORECASE)
        
        # Remove STATUS commands
        text = re.sub(r'STATUS:[^\s]*', '', text, flags=re.IGNORECASE)
        
        # Clean up multiple spaces, line breaks, and punctuation issues
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)  # Remove spaces before punctuation
        text = re.sub(r'\.+', '.', text)  # Replace multiple periods with single period
        text = re.sub(r'\s+$', '', text)  # Remove trailing whitespace
        text = re.sub(r'^\s+', '', text)  # Remove leading whitespace
        
        # Fix cases where punctuation is removed with the command
        text = re.sub(r'(\w)\s+([.,;:!?])', r'\1\2', text)  # Fix space between word and punctuation
        
        # Log if there were any changes
        if text != original_text and self.debug_mode:
            self.log(f"Cleaned text for speech:\nBEFORE: {original_text}\nAFTER: {text}")
        
        return text.strip()
    
    def text_to_speech(self, text, ref_audio_path=None, prompt_text=None, prompt_lang=None, 
                       text_lang="en", play_audio=True, clean_commands=True):
        """
        Convert text to speech using GPT-SoVITS API
        
        Args:
            text (str): Text to convert to speech
            ref_audio_path (str): Path to reference audio file (optional, uses default if None)
            prompt_text (str): Text content of the reference audio (optional, uses default if None)
            prompt_lang (str): Language of the reference audio (optional, uses default if None)
            text_lang (str): Language of the input text (en, zh, etc.)
            play_audio (bool): Whether to play the audio immediately
            clean_commands (bool): Whether to remove commands from the text
            
        Returns:
            str: Path to the saved audio file
        """
        try:
            # Use default reference if not provided
            if ref_audio_path is None:
                ref_audio_path = self.default_ref_audio
            if prompt_text is None:
                prompt_text = self.default_prompt_text
            if prompt_lang is None:
                prompt_lang = self.default_prompt_lang
            
            # Check if reference audio is available
            if ref_audio_path is None or prompt_text is None:
                print("ERROR: Reference audio is required for GPT-SoVITS")
                print("Use set_default_reference() or provide ref_audio_path and prompt_text")
                return None
                
            # Clean the text if requested
            if clean_commands:
                speech_text = self.clean_for_speech(text)
                if not speech_text:
                    print("WARNING: Text is empty after cleaning commands")
                    return None
            else:
                speech_text = text
            
            # Construct the URL with query parameters
            params = {
                "refer_wav_path": ref_audio_path,
                "prompt_text": prompt_text,
                "prompt_language": prompt_lang,
                "text": speech_text,
                "text_language": text_lang,
                "top_k": 15,
                "top_p": 1,
                "temperature": 1,
                "speed": 1
            }
            
            # Construct the full URL
            url = f"{self.api_url}/?" + urllib.parse.urlencode(params)
            self.log(f"Sending TTS request to: {url}")
            
            # Send the GET request
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"Error from TTS API: {response.status_code} - {response.text}")
                return None
            
            # Process the audio response
            audio_data = response.content
            
            # Save to both the timestamped file (for debugging) and the latest file
            timestamp_file = os.path.join(self.audio_dir, f"tts_output_{int(time.time())}.wav")
            
            # For debugging: save a timestamped version
            if self.debug_mode:
                with open(timestamp_file, "wb") as f:
                    f.write(audio_data)
                self.log(f"Debug copy saved to {timestamp_file}")
            
            # Always save to the latest file (overwriting previous)
            with open(self.latest_output_file, "wb") as f:
                f.write(audio_data)
            
            self.log(f"Audio saved to {self.latest_output_file}")
            
            # Play the audio if requested
            if play_audio:
                self.play_audio_data(audio_data)
            
            # Return the path to the latest file
            return self.latest_output_file
                
        except Exception as e:
            print(f"Error in text_to_speech: {e}")
            return None
    
    def play_audio_data(self, audio_data):
        """
        Play audio data using pygame
        
        Args:
            audio_data (bytes): Audio data to play
        """
        try:
            # Create a BytesIO object from the audio data
            audio_io = BytesIO(audio_data)
            
            # Load and play the audio
            pygame.mixer.music.load(audio_io)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            self.log("Finished playing audio")
            
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def play_audio_file(self, audio_file):
        """
        Play an audio file using pygame
        
        Args:
            audio_file (str): Path to the audio file
        """
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            self.log("Finished playing audio file")
            
        except Exception as e:
            print(f"Error playing audio file: {e}")

# Test the TTS functionality
def test_tts():
    # Create a TTS handler with debug mode enabled
    tts = TTSHandler(debug_mode=True)
    
    # Use the default hard-coded reference - no need to ask for input
    print(f"Using reference audio: {tts.default_ref_audio}")
    print(f"Prompt text: {tts.default_prompt_text}")
    print(f"Prompt language: {tts.default_prompt_lang}")
    
    # Test with some demo text
    demo_text = "Hello, I am your smart home assistant. I can control your lights and TV. LIGHT:wiz:ON:brightness=75:color=240,100 TV:ON"
    
    print(f"Converting the following text to speech: '{demo_text}'")
    print("Cleaning commands...")
    cleaned_text = tts.clean_for_speech(demo_text)
    print(f"Cleaned text: '{cleaned_text}'")
    
    audio_file = tts.text_to_speech(demo_text, text_lang="en", clean_commands=True)
    
    if audio_file:
        print(f"TTS test successful! Audio saved to: {audio_file}")
    else:
        print("TTS test failed.")

if __name__ == "__main__":
    test_tts() 