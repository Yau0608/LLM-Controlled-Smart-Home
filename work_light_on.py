from homeassistant_api import Client
import time

def test_home_controls():
    # Replace with your token
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZDBhYzc2N2MxZmY0YTY4YjY0Zjc5M2JmOTA0Y2IyMSIsImlhdCI6MTc0MjE5ODc2NCwiZXhwIjoyMDU3NTU4NzY0fQ.e4fsrfHSNlWbI-HLB2nAQv8HhdXk2SFu8nJRcOtaJj4"
    
    # Replace with your Raspberry Pi's IP address
    RASPBERRY_PI_IP = "192.168.0.171"  # Update this with your actual Home Assistant IP
    
    client = Client(f"http://{RASPBERRY_PI_IP}:8123/api", TOKEN)

    try:
        # Test 1: Simple light control
        print("Test 1: Basic light control...")
        try:
            # Just try to turn on the light with minimal parameters
            response = client.request(
                method="post",
                path="services/light/turn_on",
                json={
                    "entity_id": "light.entrance_color_white_lights"
                }
            )
            print(f"Response: {response}")
            print("Success!")
        except Exception as e:
            print(f"Failed: {e}")
            print(f"Error type: {type(e)}")
            print(f"Error args: {e.args}")
            
        # Test 2: Control WiZ light if available
        print("\nTest 2: WiZ light control...")
        try:
            # Try to turn on the WiZ light
            response = client.request(
                method="post",
                path="services/light/turn_on",
                json={
                    "entity_id": "light.wiz_rgbw_tunable_bd2b10",
                    "brightness": 128,  # 50% brightness (0-255)
                    "hs_color": [240, 100]  # Blue color
                }
            )
            print(f"Response: {response}")
            print("Success!")
        except Exception as e:
            print(f"Failed: {e}")
            print(f"Error type: {type(e)}")
            print(f"Error args: {e.args}")

    except Exception as e:
        print(f"Main error: {e}")
        print("\nPlease verify:")
        print("1. Home Assistant is running on your Raspberry Pi")
        print("2. Your token is correct")
        print(f"3. You can access http://{RASPBERRY_PI_IP}:8123 in your browser")
        print("4. The Raspberry Pi IP address is correct")

if __name__ == "__main__":
    test_home_controls() 