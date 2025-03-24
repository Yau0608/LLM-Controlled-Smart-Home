from speech_recognition import SpeechRecognizer
from llm_handler import LLMHandler
import keyboard
import time

def main():
    # Initialize components
    print("Initializing components...")
    speech_recognizer = SpeechRecognizer()
    llm_handler = LLMHandler(debug_mode=False)  # Disable debug output by default
    print("System ready!")

    while True:
        print("\n=== Ready for new command ===")
        print("Options:")
        print("- Press and hold SPACE to record your voice command")
        print("- Press 't' to type your command")
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