from speech_recognition import SpeechRecognizer
from llm_handler import LLMHandler
from tts_handler import TTSHandler
import keyboard
import time
import os

def main():
    # Initialize components
    print("Initializing components...")
    speech_recognizer = SpeechRecognizer()
    llm_handler = LLMHandler(debug_mode=False)  # Disable debug output by default
    tts_handler = TTSHandler(debug_mode=False)  # Initialize TTS handler with default parameters
    
    # The TTSHandler already has the default reference audio configured
    print("System ready!")

    # Voice response flag - enable by default
    voice_response_enabled = True

    while True:
        print("\n=== Ready for new command ===")
        print("Options:")
        print("- Press and hold SPACE to record your voice command")
        print("- Press 't' to type your command")
        print("- Press 'v' to toggle voice response", f"(currently {'enabled' if voice_response_enabled else 'disabled'})")
        print("- Press 'q' to quit")
        
        # Wait for input choice
        while True:
            if keyboard.is_pressed('space'):
                transcribed_text = speech_recognizer.record_and_transcribe()
                break
            elif keyboard.is_pressed('t'):
                print("\nEnter your command:")
                transcribed_text = input("> ")
                break
            elif keyboard.is_pressed('v'):
                voice_response_enabled = not voice_response_enabled
                status = "enabled" if voice_response_enabled else "disabled"
                print(f"\nVoice response {status}")
                time.sleep(0.5)  # Prevent multiple toggles
            elif keyboard.is_pressed('q'):
                print("\nGoodbye!")
                return
            time.sleep(0.1)

        print(f"\nCommand: {transcribed_text}")
        
        # Process with LLM
        print("\nProcessing with LLM...")
        parsed_responses = llm_handler.send_prompt(transcribed_text)
        
        # Extract and show only the main response content
        response_text = ""
        for resp in parsed_responses:
            response_text = resp.get("response", "")
        
        # Display a cleaner format focusing on the response
        print("\nResponse:")
        print("-" * 40)
        print(response_text)
        print("-" * 40)

        # Process and execute the command using the already fetched response
        result = llm_handler.process_command_from_responses(parsed_responses)
        print(f"Action: {result}")
        
        # Generate voice response if enabled
        if voice_response_enabled and response_text:
            print("\nGenerating voice response...")
            # No need for a separate clean_for_speech call - the TTS handler will do this internally
            audio_file = tts_handler.text_to_speech(response_text, text_lang="en", clean_commands=True)
            
            if audio_file:
                print(f"Voice response played and saved to: {audio_file}")
            else:
                print("Failed to generate voice response.")
        
        # Options menu
        print("\nOptions:")
        print("- Press 'r' to enter another command")
        print("- Press 'q' to quit")
        
        while True:
            if keyboard.is_pressed('r'):
                break
            if keyboard.is_pressed('q'):
                print("\nGoodbye!")
                return
            time.sleep(0.1)

if __name__ == "__main__":
    main() 