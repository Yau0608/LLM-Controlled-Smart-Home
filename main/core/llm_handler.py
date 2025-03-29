import sys
from pathlib import Path
import colorsys

# Add the task directory to the path
task_dir = Path(__file__).parent.parent / 'task'
sys.path.append(str(task_dir))

import requests
import json
from smart_home_control import SmartHomeControl

class LLMHandler:
    def __init__(self, debug_mode=False):
        self.base_dir = Path(__file__).parent
        self.debug_mode = debug_mode
        self.home_control = SmartHomeControl("API")
        self.system_prompt = """You are a smart home control assistant. You control a WiZ RGBW Tunable light and a 4K TV.

    IMPORTANT: When responding to control requests, ALWAYS use clear command formatting:
    
    1. First provide your natural language response
    2. Then add a line break
    3. Then provide commands on separate lines
    
    Light control command formats:
    - LIGHT:wiz:OFF
    - LIGHT:wiz:ON:brightness=75
    - LIGHT:wiz:ON:brightness=50:color=240,100
    
    Color format is HSL with hue (0-360) and saturation (0-100) values separated by a comma.
    Common colors:
    - Red: color=0,100
    - Green: color=120,100
    - Blue: color=240,100
    - Yellow: color=60,100
    - Purple: color=270,100
    - Orange: color=30,100
    - Pink: color=300,100
    
    TV control command formats:
    - TV:ON
    - TV:OFF
    
    For status requests, use:
    - STATUS:ALL
    
    Example of correct response format:
    "I'll turn on the light to a nice blue color and turn on the TV.
    
    LIGHT:wiz:ON:brightness=75:color=240,100
    TV:ON"
    
    For multiple light colors in sequence, put each command on its own line:
    "I'll create a rainbow effect with the lights.
    
    LIGHT:wiz:ON:brightness=50:color=0,100
    LIGHT:wiz:ON:brightness=50:color=120,100
    LIGHT:wiz:ON:brightness=50:color=240,100"
    
    Always include a natural language response first, followed by the commands on separate lines."""

    def log(self, message):
        """Print debug messages only if debug mode is enabled"""
        if self.debug_mode:
            print(f"DEBUG: {message}")

    def send_prompt(self, prompt, max_tokens=1024):
        try:
            url = "http://localhost:11434/api/generate"
            headers = {
                "Content-Type": "application/json"
            }
            
            formatted_prompt = f"{self.system_prompt}\n\nUser: {prompt}\nAssistant:"
            
            data = {
                "model": "gemma3:12b",
                "prompt": formatted_prompt,
                "max_tokens": max_tokens,
                "system": self.system_prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data)
            response_json = json.loads(response.text)
            return [response_json]

        except Exception as e:
            print(f"Error in send_prompt: {e}")
            return []

    def analyze_llm_response(self, parsed_responses):
        try:
            response_text = "".join([item["response"] for item in parsed_responses])
            
            # Extract commands from response
            commands = []
            for line in response_text.splitlines():
                if "LIGHT:" in line:
                    commands.append(("light", line))
                elif "TV:" in line:
                    commands.append(("tv", line))
                elif "STATUS:" in line:
                    commands.append(("status", line))
            
            return commands if commands else None

        except Exception as e:
            print(f"Error in analyze_llm_response: {e}")
            return None
            
    def rgb_to_hsl(self, r, g, b):
        """Convert RGB color values to HSL format expected by Home Assistant"""
        # Normalize RGB values to 0-1 range
        r = r / 255
        g = g / 255
        b = b / 255
        
        # Convert to HSL
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        
        # Convert to degrees and percentage
        h = round(h * 360)  # 0-360 degrees
        s = round(s * 100)  # 0-100%
        
        self.log(f"Converted RGB({r*255},{g*255},{b*255}) to HSL({h},{s})")
        return h, s

    def execute_command(self, command):
        try:
            command_type, command_text = command
            
            if command_type == "light":
                # Extract the command portion (everything starting with LIGHT:)
                if "LIGHT:" not in command_text:
                    return "Command format incorrect"
                
                # Clean up the command - should be cleaner now that it's on its own line
                command_pattern = command_text.strip()
                
                parts = command_pattern.split(":")
                self.log(f"Cleaned command parts: {parts}")
                
                # Check if "wiz" or "rgb" is in the parts (the light names we care about)
                if "wiz" in parts or "rgb" in parts:
                    # Find the light name
                    if "wiz" in parts:
                        light_name = "wiz"
                    else:
                        light_name = "rgb"
                    
                    # Check if it's ON or OFF command
                    if "OFF" in parts or "off" in parts:
                        return self.home_control.control_light(light_name, "off")
                    elif "ON" in parts or "on" in parts:
                        brightness = None
                        color = None
                        
                        # Parse brightness and color
                        for part in parts:
                            if part.lower().startswith("brightness="):
                                try:
                                    brightness_str = part.split("=")[1].strip('"')
                                    brightness = int(brightness_str)
                                except (ValueError, IndexError) as e:
                                    self.log(f"Error parsing brightness: {e}")
                                    brightness = 50  # Default to 50% brightness
                            elif part.lower().startswith("color="):
                                try:
                                    color_str = part.split("=")[1].strip('"')
                                    color_values = [int(x) for x in color_str.split(",")]
                                    
                                    # Handle different color formats
                                    if len(color_values) == 2:
                                        # Already in HSL (hue, saturation) format
                                        hue, sat = color_values
                                        color = (hue, sat)
                                        self.log(f"Using HSL color: {color}")
                                    elif len(color_values) == 3:
                                        # RGB format, convert to HSL
                                        r, g, b = color_values
                                        hue, sat = self.rgb_to_hsl(r, g, b)
                                        color = (hue, sat)
                                        self.log(f"Converted RGB to HSL color: {color}")
                                    else:
                                        self.log(f"Unrecognized color format: {color_values}")
                                        # Default to white if format is unrecognized
                                        color = (0, 0)
                                except (ValueError, IndexError) as e:
                                    self.log(f"Error parsing color: {e}")
                                    # If we can't parse the color, default to white
                                    color = (0, 0)
                        
                        return self.home_control.control_light(light_name, "on", brightness, color)
                    else:
                        # Default to turning on if neither ON nor OFF is specified
                        self.log("Neither ON nor OFF found in command, defaulting to ON")
                        return self.home_control.control_light(light_name, "on")
                else:
                    # Default to wiz if no light name is found
                    return self.home_control.control_light("wiz", "on")
            
            elif command_type == "tv":
                return self.home_control.control_tv(command_text)
            
            elif command_type == "status":
                return self.home_control.get_status()
            
            return "Command not recognized"

        except Exception as e:
            print(f"Error in execute_command: {e}")
            return f"Error executing command: {str(e)}"

    def process_command_from_responses(self, responses):
        """Process commands from previously fetched LLM responses"""
        try:
            results = []
            
            for response in responses:
                response_text = response.get("response", "")
                self.log(f"Processing response: {response_text}")
                
                # Find all command patterns
                commands = []
                
                # Split response by lines and look for command lines
                lines = response_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith("LIGHT:"):
                        commands.append(("light", line))
                    elif line.startswith("TV:"):
                        if line.startswith("TV:ON"):
                            commands.append(("tv", "on"))
                        elif line.startswith("TV:OFF"):
                            commands.append(("tv", "off"))
                    elif line.startswith("STATUS:"):
                        commands.append(("status", line))
                
                # Process all found commands
                for i, command in enumerate(commands):
                    try:
                        command_type, command_text = command
                        
                        # Handle different command types
                        if command_type == "light":
                            result = self.execute_command((command_type, command_text))
                        elif command_type == "tv":
                            result = self.home_control.control_tv(command_text)
                        elif command_type == "status":
                            result = self.execute_command((command_type, command_text))
                        else:
                            result = f"Unknown command type: {command_type}"
                            
                        results.append(result)
                        
                        # Add a delay between commands if there are multiple
                        if len(commands) > 1:
                            import time
                            print(f"Command {i+1} of {len(commands)} completed: {result}")
                            if i < len(commands) - 1:
                                time.sleep(2)  # 2-second delay between commands
                            
                    except Exception as e:
                        self.log(f"Error executing command {command}: {e}")
            
            # If no commands were found, return the natural language response
            if not results:
                return "I understand, but I don't see any actions to take."
            
            # Return all results joined together
            return " | ".join(str(r) for r in results)

        except Exception as e:
            print(f"Error in process_command_from_responses: {e}")
            return f"Error processing command: {str(e)}"

    def process_request(self, text):
        """Legacy method - kept for backwards compatibility"""
        try:
            responses = self.send_prompt(text)
            return self.process_command_from_responses(responses)
        except Exception as e:
            print(f"Error in process_request: {e}")
            return f"Error processing request: {str(e)}" 