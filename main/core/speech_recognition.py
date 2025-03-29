import whisper
import torch
import pyaudio
import wave
import keyboard
import pyperclip
from datetime import datetime

class SpeechRecognizer:
    def __init__(self):
        self.model = whisper.load_model("small")
        
    def record_audio(self, filename="temp_recording.wav", sample_rate=16000):
        # Audio recording parameters
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=sample_rate,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        print("Press and hold SPACE to record, release to stop...")
        frames = []
        
        keyboard.wait('space')
        print("Recording... (Release SPACE to stop)")
        
        while keyboard.is_pressed('space'):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("Recording stopped!")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return filename

    def record_and_transcribe(self):
        temp_file = self.record_audio()
        result = self.model.transcribe(temp_file, language="en")
        transcribed_text = result['text']
        
        # Save to file and clipboard
        with open("latest_transcription.txt", "w", encoding='utf-8') as f:
            f.write(transcribed_text)
        pyperclip.copy(transcribed_text)
        
        print("Text has been copied to clipboard and saved to latest_transcription.txt!")
        return transcribed_text 

    def transcribe_file(self, audio_file_path):
        """
        Transcribe an existing audio file
        
        Args:
            audio_file_path (str): Path to the audio file to transcribe
            
        Returns:
            str: The transcribed text
        """
        try:
            print(f"Transcribing file: {audio_file_path}")
            result = self.model.transcribe(audio_file_path, language="en")
            transcribed_text = result['text']
            
            # Save to file and clipboard for consistency
            with open("latest_transcription.txt", "w", encoding='utf-8') as f:
                f.write(transcribed_text)
            
            print(f"Transcription complete: {transcribed_text}")
            return transcribed_text
            
        except Exception as e:
            print(f"Error transcribing file: {e}")
            return f"Error during transcription: {str(e)}"

