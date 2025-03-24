from homeassistant_api import Client
import json

def test_connection():
    # Replace with your token
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZDBhYzc2N2MxZmY0YTY4YjY0Zjc5M2JmOTA0Y2IyMSIsImlhdCI6MTc0MjE5ODc2NCwiZXhwIjoyMDU3NTU4NzY0fQ.e4fsrfHSNlWbI-HLB2nAQv8HhdXk2SFu8nJRcOtaJj4"
    
    # Replace with your Raspberry Pi's IP address
    RASPBERRY_PI_IP = "192.168.0.171"  # Update this with your actual Raspberry Pi IP
    
    try:
        # Create client connecting to the Raspberry Pi
        client = Client(f"http://{RASPBERRY_PI_IP}:8123/api", TOKEN)
        
        # Test connection by getting states
        states = client.get_states()
        print("Successfully connected to Home Assistant!")
        
        # Print some test entities
        print("\nFound these entities:")
        for state in states:
            if state.entity_id.startswith(('light.', 'climate.')):
                print(f"Entity: {state.entity_id}")
                print(f"State: {state.state}")
                print("---")
                
        # Specifically check for the WiZ light
        wiz_light = next((s for s in states if s.entity_id == "light.wiz_rgbw_tunable_bd2b10"), None)
        if wiz_light:
            print("\nFound your WiZ light:")
            print(f"Entity: {wiz_light.entity_id}")
            print(f"State: {wiz_light.state}")
            print(f"Attributes: {wiz_light.attributes}")
        else:
            print("\nCouldn't find your WiZ light. Check the entity ID.")
                
    except Exception as e:
        print(f"Connection error: {e}")
        print("\nPlease verify:")
        print("1. Home Assistant is running on your Raspberry Pi")
        print("2. Your token is correct")
        print(f"3. You can access http://{RASPBERRY_PI_IP}:8123 in your browser")
        print("4. The Raspberry Pi IP address is correct")
        print("5. There are no firewall issues blocking the connection")

if __name__ == "__main__":
    test_connection() 