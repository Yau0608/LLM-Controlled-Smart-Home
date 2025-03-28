from homeassistant_api import Client
import time

class SmartHomeControl:
    """
    Smart Home Control Interface for Home Assistant
    
    Currently Supported Devices and Functions:
    
    1. WiZ RGBW Tunable Light Control (entity_id: light.wiz_rgbw_tunable_bd2b10)
       Methods:
       - control_light(light_name, state="on"|"off", brightness=0-100, color=(hue,saturation))
         * light_name: Name of the light or alias ("wiz" or "rgb")
         * state: "on" or "off"
         * brightness: percentage from 0-100, converted to 0-255 internally
         * color: tuple of (hue: 0-360, saturation: 0-100)
         Examples:
         - Turn on: control_light("wiz", "on")
         - Set brightness: control_light("wiz", "on", brightness=50)
         - Set color: control_light("wiz", "on", brightness=100, color=(240,100))  # Blue
         - Turn off: control_light("wiz", "off")
    
    2. TV Control (entity_id: remote.4ktv_jup)
       Methods:
       - control_tv(action="on"|"off")
         * action: "on" or "off"
         Examples:
         - Turn on: control_tv("on")
         - Turn off: control_tv("off")

    3. Status Monitoring
       Methods:
       - get_status()
         Returns current state of the WiZ light including:
         * state, brightness, color
    """
    
    def __init__(self, token):
        """Initialize connection to Home Assistant"""
        # Use the working Raspberry Pi IP address
        RASPBERRY_PI_IP = "192.168.0.171"  # Your Home Assistant IP
        
        self.client = Client(f"http://{RASPBERRY_PI_IP}:8123/api", token)
        
        # Add a light name mapping for easier reference
        self.light_aliases = {
            "wiz": "wiz_rgbw_tunable_bd2b10",
            "rgb": "wiz_rgbw_tunable_bd2b10",
            # Add more aliases as needed
        }
        
        # Store the entity ID for easy reference
        self.wiz_entity_id = "light.wiz_rgbw_tunable_bd2b10"
        self.tv_entity_id = "remote.4ktv_jup"
    
    def control_light(self, light_name, state, brightness=None, color=None):
        """
        Control the WiZ light using name or alias
        
        Args:
            light_name (str): Name or alias of the light ("wiz", "rgb")
            state (str): "on" or "off"
            brightness (int, optional): 0-100 (will be converted to 0-255)
            color (tuple, optional): (hue: 0-360, saturation: 0-100)
        
        Returns:
            str: Status message
        """
        # This is a simplified wrapper for the control_specific_light method
        return self.control_specific_light(light_name, state, brightness, color)

    def control_specific_light(self, light_name, state, brightness=None, color=None):
        """Control a specific light by entity ID or alias"""
        try:
            # Convert alias to actual entity ID if it exists in the mapping
            if light_name in self.light_aliases:
                light_name = self.light_aliases[light_name]
            
            # Construct the full entity ID
            entity_id = f"light.{light_name}" if not light_name.startswith("light.") else light_name
            
            if state == "off":
                self.client.request(
                    method="post",
                    path="services/light/turn_off",
                    json={"entity_id": entity_id}
                )
                return f"Turned off {light_name}"
            
            elif state == "on":
                # Base parameters
                data = {"entity_id": entity_id}
                
                # Add brightness if provided
                if brightness is not None:
                    # Convert 0-100 scale to 0-255 for Home Assistant
                    data["brightness"] = int(brightness * 255 / 100)
                
                # Add color if provided
                if color is not None:
                    hue, saturation = color
                    # Home Assistant expects HSL values
                    data["hs_color"] = [hue, saturation]
                
                self.client.request(
                    method="post",
                    path="services/light/turn_on",
                    json=data
                )
                
                status_msg = f"Turned on {light_name}"
                if brightness is not None:
                    status_msg += f" at {brightness}% brightness"
                if color is not None:
                    status_msg += f" with color {color}"
                return status_msg
            
        except Exception as e:
            return f"Error controlling {light_name}: {str(e)}"

    def control_tv(self, action):
        """
        Control the TV
        
        Args:
            action (str): "on" or "off"
        
        Returns:
            str: Status message
        """
        try:
            if action.lower() == "on":
                self.client.request(
                    method="post",
                    path="services/remote/turn_on",
                    json={"entity_id": self.tv_entity_id}
                )
                return f"Turned on TV"
            
            elif action.lower() == "off":
                self.client.request(
                    method="post",
                    path="services/remote/turn_off",
                    json={"entity_id": self.tv_entity_id}
                )
                return f"Turned off TV"
            
            else:
                return f"Unknown TV action: {action}"
                
        except Exception as e:
            return f"Error controlling TV: {str(e)}"

    def get_status(self):
        """
        Get current status of the WiZ light
        
        Returns:
            dict: Current state and attributes of the WiZ light
        """
        try:
            # Get the state of the WiZ light
            light = self.client.get_state(entity_id=self.wiz_entity_id)
            
            # Format and return the status
            status = {
                "light": {
                    "state": light.state,
                    "brightness": light.attributes.get("brightness"),
                    "color": light.attributes.get("hs_color"),
                    "entity_id": self.wiz_entity_id
                }
            }
            return status
            
        except Exception as e:
            return f"Error getting status: {str(e)}"

# Test the controls for the WiZ light only
def test_controls():
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZDBhYzc2N2MxZmY0YTY4YjY0Zjc5M2JmOTA0Y2IyMSIsImlhdCI6MTc0MjE5ODc2NCwiZXhwIjoyMDU3NTU4NzY0fQ.e4fsrfHSNlWbI-HLB2nAQv8HhdXk2SFu8nJRcOtaJj4"
    home = SmartHomeControl(TOKEN)
    
    # Test WiZ light controls
    print("\nTesting WiZ light controls:")
    print("1. Turning on WiZ light at full brightness")
    print(home.control_light("wiz", "on", brightness=100))  # Full brightness
    time.sleep(2)
    
    print("\n2. Setting WiZ light to blue at 50% brightness")
    print(home.control_light("wiz", "on", brightness=50, color=(240, 100)))  # Blue at 50%
    time.sleep(2)
    
    print("\n3. Turning off WiZ light")
    print(home.control_light("wiz", "off"))
    time.sleep(2)
    
    # Get status
    print("\nCurrent WiZ light status:")
    print(home.get_status())

if __name__ == "__main__":
    test_controls() 