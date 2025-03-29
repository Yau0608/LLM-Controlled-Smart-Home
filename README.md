# Voice Command System - Installation Guide

## System Requirements
- Python 3.9 or 3.10
- Conda or Miniconda
- FFmpeg (system dependency for Whisper)

## Setup Instructions

### 1. Install Conda (if not already installed)
Download and install from: https://docs.conda.io/en/latest/miniconda.html

### 2. Create and activate a conda environment
```bash
# Create new environment
conda create -n voice_command python=3.9
# Activate the environment
conda activate voice_command
```

Alternatively, you can use the provided environment.yml file:
```bash
conda env create -f environment.yml
conda activate voice_command
```

### 3. Install PyTorch
```bash
# CPU-only version
conda install pytorch cpuonly -c pytorch
# OR for CUDA support (if you have an NVIDIA GPU)
# conda install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia
```

### 4. Install OpenAI Whisper
```bash
pip install -U openai-whisper
```

### 5. Install FFmpeg (System Dependency)
#### Windows:
- Download from: https://ffmpeg.org/download.html
- Add to system PATH

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg

#### macOS:
```bash
brew install ffmpeg
```

#### Linux:
```bash
sudo apt update && sudo apt install ffmpeg
```

### 6. Install other required packages
```bash
pip install pyaudio keyboard pyperclip requests homeassistant-api flask
```

Alternatively, you can use the provided requirements.txt file:
```bash
pip install -r requirements.txt
```

### 7. Install Ollama for LLM functionality
Follow instructions at: https://ollama.com/download

### 8. Pull the required model
After installing Ollama, run:
```bash
ollama pull llama3:8b
```

For GPU users with limited VRAM, use a smaller model such as:
```bash
ollama pull gemma2:7b 
```

### 9. Configure Home Assistant
Refer to the `home_assistant_setup.md` file for detailed instructions on setting up Home Assistant for this project.

### 10. Run the application
```bash
# Navigate to project directory
cd main/core
# Start the application
python run.py
```

### 11. Mobile Interface (NEW!)
You can now control your smart home from your phone's browser:
```bash
# Navigate to project directory
cd main/core
# Start the mobile web interface
python run_mobile.py
```
Then access the displayed URL from any phone on the same WiFi network.
See `main/mobile_interface.md` for detailed instructions.

## Troubleshooting

### PyAudio Installation Issues
If you encounter issues installing PyAudio:

#### Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

#### macOS:
```bash
brew install portaudio
pip install pyaudio
```

#### Linux:
```bash
sudo apt-get install python3-pyaudio
# OR
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Permission Issues
If you encounter permission issues with keyboard module:
- On Linux, you may need to run the script with sudo
- On macOS, you might need to grant accessibility permissions

## Note
Make sure Ollama is running in the background before starting the application.
Make sure Home Assistant is properly configured and running for smart home control functionality. 
