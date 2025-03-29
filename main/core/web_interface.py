from flask import Flask, request, jsonify, send_file, render_template_string, make_response
import os
import time
from pathlib import Path
import socket
import glob

# Import the existing components
from speech_recognition import SpeechRecognizer
from llm_handler import LLMHandler
from tts_handler import TTSHandler

app = Flask(__name__)

# Initialize the components
speech_recognizer = SpeechRecognizer()
llm_handler = LLMHandler(debug_mode=False)
tts_handler = TTSHandler(debug_mode=False)

# Directory to store temporary audio files
TEMP_DIR = Path(__file__).parent / "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def cleanup_mobile_recordings(keep_latest=True):
    """Clean up mobile recording files, optionally keeping the most recent one"""
    try:
        # Find all mobile recording files
        mobile_files = glob.glob(os.path.join(TEMP_DIR, "mobile_recording_*.wav"))
        
        # Sort by creation time (newest last)
        mobile_files.sort(key=os.path.getctime)
        
        # If we should keep the latest and there are files, remove it from the list
        if keep_latest and mobile_files:
            latest_file = mobile_files.pop()
            print(f"Keeping latest recording: {os.path.basename(latest_file)}")
            
        # Delete all others
        for file in mobile_files:
            try:
                os.remove(file)
                print(f"Deleted old recording: {os.path.basename(file)}")
            except Exception as e:
                print(f"Could not delete file {file}: {e}")
    except Exception as e:
        print(f"Error cleaning up mobile recordings: {e}")
    
# Clean up any old recordings from previous runs
cleanup_mobile_recordings(keep_latest=True)

# HTML template for the mobile interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Voice Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            text-align: center;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
        }
        #recordButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 20px 2px;
            cursor: pointer;
            border-radius: 50px;
            width: 200px;
            height: 200px;
            border-radius: 100px;
            transition: all 0.3s;
        }
        #recordButton:active {
            background-color: #FF5722;
            transform: scale(0.95);
        }
        #status {
            margin-top: 20px;
            color: #666;
        }
        #response {
            margin-top: 20px;
            padding: 10px;
            background-color: #e9e9e9;
            border-radius: 5px;
            display: none;
        }
        #textInputContainer {
            margin-top: 20px;
            display: none;
        }
        #textInput {
            padding: 10px;
            width: 80%;
            max-width: 400px;
            margin-bottom: 10px;
        }
        #sendTextButton {
            padding: 10px 20px;
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>Smart Home Voice Control</h1>
    <div id="voiceContainer">
        <button id="recordButton">Hold to Speak</button>
    </div>
    
    <div id="textInputContainer">
        <p>Voice recording not available. Please type your command instead:</p>
        <input type="text" id="textInput" placeholder="Type your command...">
        <button id="sendTextButton">Send</button>
    </div>
    
    <button id="testButton" style="margin-top: 20px; padding: 10px;">Test Connection</button>
    <div id="status">Ready</div>
    <div id="response"></div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        const recordButton = document.getElementById('recordButton');
        const statusDiv = document.getElementById('status');
        const responseDiv = document.getElementById('response');
        const textInputContainer = document.getElementById('textInputContainer');
        const textInput = document.getElementById('textInput');
        const sendTextButton = document.getElementById('sendTextButton');
        let currentAudio = null; // Track current audio playback

        // Setup recording when page loads
        document.addEventListener('DOMContentLoaded', setupInput);

        function setupInput() {
            // Check if mediaDevices is supported
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                setupRecording();
            } else {
                // Fallback to text input if microphone access is not available
                statusDiv.textContent = "Microphone access not available on HTTP. Using text input instead.";
                textInputContainer.style.display = "block";
                document.getElementById('voiceContainer').style.display = "none";
            }
        }

        function setupRecording() {
            statusDiv.textContent = "Requesting microphone...";
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    statusDiv.textContent = "Microphone access granted!";
                    
                    // Try different MIME types until one works
                    let options = {};
                    const mimeTypes = [
                        'audio/webm',
                        'audio/mp4',
                        'audio/ogg',
                        ''  // empty string = browser default
                    ];
                    
                    // Find the first supported MIME type
                    for (let type of mimeTypes) {
                        try {
                            if (type && MediaRecorder.isTypeSupported(type)) {
                                options = { mimeType: type };
                                statusDiv.textContent += ` Using ${type}`;
                                break;
                            }
                        } catch (e) {
                            // Continue to next type
                        }
                    }
                    
                    try {
                        mediaRecorder = new MediaRecorder(stream, options);
                        
                        mediaRecorder.ondataavailable = (event) => {
                            audioChunks.push(event.data);
                        };
                        
                        mediaRecorder.onstop = () => {
                            sendAudioToServer();
                        };
                        
                        statusDiv.textContent = "Ready - Hold the button to speak";
                    } catch (err) {
                        statusDiv.textContent = "Failed to create recorder: " + err;
                        // Fallback to text input
                        textInputContainer.style.display = "block";
                    }
                })
                .catch(error => {
                    statusDiv.textContent = "Error accessing microphone: " + error;
                    // Fallback to text input
                    textInputContainer.style.display = "block";
                });
        }

        // Touch events for mobile
        recordButton.addEventListener('touchstart', startRecording);
        recordButton.addEventListener('touchend', stopRecording);
        // Mouse events for testing on desktop
        recordButton.addEventListener('mousedown', startRecording);
        recordButton.addEventListener('mouseup', stopRecording);
        
        function startRecording(e) {
            e.preventDefault();
            statusDiv.textContent = "Button pressed";
            if (mediaRecorder && !isRecording) {
                try {
                    audioChunks = [];
                    mediaRecorder.start();
                    isRecording = true;
                    recordButton.textContent = "Recording...";
                    statusDiv.textContent = "Recording started!";
                    recordButton.style.backgroundColor = "#FF5722";
                    responseDiv.style.display = "none";
                } catch(err) {
                    statusDiv.textContent = "Error starting recording: " + err;
                }
            } else {
                statusDiv.textContent = "Can't record: " + (mediaRecorder ? "Already recording" : "No recorder");
            }
        }
        
        function stopRecording(e) {
            e.preventDefault();
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                recordButton.textContent = "Hold to Speak";
                statusDiv.textContent = "Processing...";
                recordButton.style.backgroundColor = "#4CAF50";
            }
        }
        
        function sendAudioToServer() {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio', audioBlob);
            
            fetch('/upload_audio', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                statusDiv.textContent = data.status;
                
                if (data.text) {
                    responseDiv.textContent = data.text;
                    responseDiv.style.display = "block";
                }
                
                if (data.audio_url) {
                    // Stop any existing audio playback
                    if (currentAudio) {
                        currentAudio.pause();
                        currentAudio = null;
                    }
                    
                    // Create and play new audio with error handling
                    currentAudio = new Audio(data.audio_url);
                    currentAudio.onerror = function(e) {
                        statusDiv.textContent = "Error playing audio: " + e;
                    };
                    currentAudio.onended = function() {
                        statusDiv.textContent = "Ready for next command";
                    };
                    currentAudio.play().catch(e => {
                        statusDiv.textContent = "Error starting playback: " + e;
                    });
                }
            })
            .catch(error => {
                statusDiv.textContent = "Error: " + error;
            });
        }

        // Add event listener for the text input button
        sendTextButton.addEventListener('click', function() {
            sendTextCommand();
        });
        
        // Also allow Enter key to submit
        textInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendTextCommand();
            }
        });
        
        function sendTextCommand() {
            const textCommand = textInput.value.trim();
            if (textCommand) {
                statusDiv.textContent = "Processing text command...";
                responseDiv.style.display = "none";
                
                fetch('/text_command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ command: textCommand })
                })
                .then(response => response.json())
                .then(data => {
                    statusDiv.textContent = data.status;
                    
                    if (data.text) {
                        responseDiv.textContent = data.text;
                        responseDiv.style.display = "block";
                    }
                    
                    if (data.audio_url) {
                        // Stop any existing audio playback
                        if (currentAudio) {
                            currentAudio.pause();
                            currentAudio = null;
                        }
                        
                        // Create and play new audio with error handling
                        currentAudio = new Audio(data.audio_url);
                        currentAudio.onerror = function(e) {
                            statusDiv.textContent = "Error playing audio: " + e;
                        };
                        currentAudio.onended = function() {
                            statusDiv.textContent = "Ready for next command";
                        };
                        currentAudio.play().catch(e => {
                            statusDiv.textContent = "Error starting playback: " + e;
                        });
                    }
                    
                    // Clear the input field
                    textInput.value = '';
                })
                .catch(error => {
                    statusDiv.textContent = "Error: " + error;
                });
            }
        }

        document.getElementById('testButton').addEventListener('click', function() {
            fetch('/test')
                .then(response => response.text())
                .then(data => {
                    statusDiv.textContent = "Test successful: " + data;
                })
                .catch(error => {
                    statusDiv.textContent = "Test failed: " + error;
                });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Add CORS headers to allow microphone access
    response = make_response(render_template_string(HTML_TEMPLATE))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    try:
        # Check if the post request has the file part
        if 'audio' not in request.files:
            return jsonify({'status': 'No audio file found'}), 400
        
        audio_file = request.files['audio']
        
        # Save the audio file
        timestamp = int(time.time())
        temp_path = os.path.join(TEMP_DIR, f"mobile_recording_{timestamp}.wav")
        audio_file.save(temp_path)
        
        # Clean up old recordings but keep this new one
        cleanup_mobile_recordings(keep_latest=True)
        
        # Process the audio through the existing pipeline
        # 1. Transcribe audio using Whisper
        transcribed_text = speech_recognizer.transcribe_file(temp_path)
        
        # 2. Process with LLM
        parsed_responses = llm_handler.send_prompt(transcribed_text)
        
        # Extract response text
        response_text = ""
        for resp in parsed_responses:
            response_text = resp.get("response", "")
        
        # 3. Execute home automation commands
        action_result = llm_handler.process_command_from_responses(parsed_responses)
        
        # 4. Generate speech response
        audio_file_path = tts_handler.text_to_speech(
            response_text, 
            play_audio=False,  # Don't play on server
            clean_commands=True
        )
        
        # Create a unique audio URL with cache-busting timestamp
        if audio_file_path:
            audio_filename = os.path.basename(audio_file_path)
            cache_buster = int(time.time() * 1000)  # Millisecond timestamp for cache busting
            audio_url = f"/audio/{audio_filename}?t={cache_buster}"
            
            return jsonify({
                'status': 'Success',
                'text': response_text,
                'action': action_result,
                'audio_url': audio_url
            })
        else:
            return jsonify({
                'status': 'Success - No audio response',
                'text': response_text,
                'action': action_result
            })
            
    except Exception as e:
        return jsonify({'status': f'Error: {str(e)}'}), 500

@app.route('/audio/<filename>')
def get_audio(filename):
    """Serve the generated audio file with no-cache headers"""
    audio_path = os.path.join(TEMP_DIR, filename)
    response = send_file(audio_path, mimetype='audio/wav')
    # Add cache control headers to prevent caching
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/test')
def test():
    return "Server connection working!"

@app.route('/text_command', methods=['POST'])
def text_command():
    try:
        # Get the text command from the request
        data = request.json
        if not data or 'command' not in data:
            return jsonify({'status': 'No command found'}), 400
        
        command_text = data['command']
        
        # 1. Process with LLM
        parsed_responses = llm_handler.send_prompt(command_text)
        
        # Extract response text
        response_text = ""
        for resp in parsed_responses:
            response_text = resp.get("response", "")
        
        # 2. Execute home automation commands
        action_result = llm_handler.process_command_from_responses(parsed_responses)
        
        # 3. Generate speech response
        audio_file_path = tts_handler.text_to_speech(
            response_text, 
            play_audio=False,  # Don't play on server
            clean_commands=True
        )
        
        # Create a unique audio URL with cache-busting timestamp
        if audio_file_path:
            audio_filename = os.path.basename(audio_file_path)
            cache_buster = int(time.time() * 1000)  # Millisecond timestamp for cache busting
            audio_url = f"/audio/{audio_filename}?t={cache_buster}"
            
            return jsonify({
                'status': 'Success',
                'text': response_text,
                'action': action_result,
                'audio_url': audio_url
            })
        else:
            return jsonify({
                'status': 'Success - No audio response',
                'text': response_text,
                'action': action_result
            })
            
    except Exception as e:
        return jsonify({'status': f'Error: {str(e)}'}), 500

def get_local_ip():
    """Get the local IP address of this machine"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def run_server(port=5000):
    """Run the Flask server"""
    local_ip = get_local_ip()
    print(f"\n===== Mobile Voice Assistant Web Interface =====")
    print(f"Server running at:")
    print(f"http://{local_ip}:{port}")
    print(f"Access this URL from your phone (must be on same WiFi network)")
    print("=================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)

def run_secure_server(port=5000):
    """Run the Flask server with HTTPS"""
    local_ip = get_local_ip()
    cert_path = Path(__file__).parent / "certificates" / "cert.pem"
    key_path = Path(__file__).parent / "certificates" / "key.pem"
    
    print(f"\n===== Secure Mobile Voice Assistant (HTTPS) =====")
    print(f"Server running at:")
    print(f"https://{local_ip}:{port}")
    print(f"Access this URL from your phone (must be on same WiFi network)")
    print("=================================================\n")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=True,
        ssl_context=(cert_path, key_path)
    )

if __name__ == "__main__":
    run_server()  # Default HTTP
    # run_secure_server()  # Comment out to prevent both servers running at once 