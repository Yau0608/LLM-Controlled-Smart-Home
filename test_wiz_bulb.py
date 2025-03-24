from main.core.llm_handler import LLMHandler

def test_commands():
    handler = LLMHandler()
    
    # Test case 1: Turn on light with brightness
    print("\nTest 1: Turn on light with brightness")
    test_command = "Turn on the light at 75% brightness"
    result = handler.process_request(test_command)
    print(f"Command: {test_command}")
    print(f"Result: {result}")
    
    # Test case 2: Turn on with color
    print("\nTest 2: Turn on light with color")
    test_command = "Set the light to blue color"
    result = handler.process_request(test_command)
    print(f"Command: {test_command}")
    print(f"Result: {result}")
    
    # Test case 3: Turn off light
    print("\nTest 3: Turn off light")
    test_command = "Turn off the light"
    result = handler.process_request(test_command)
    print(f"Command: {test_command}")
    print(f"Result: {result}")
    
if __name__ == "__main__":
    test_commands() 