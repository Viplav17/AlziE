# audio_system.py
import pyttsx3
import os
import subprocess
import time

class AudioGenerator:
    def __init__(self):
        self.audio_dir = os.path.join(os.path.dirname(__file__), 'Audio_Files')
        self._ensure_directory()
        
    def _ensure_directory(self):
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
    
    def generate_soothing_voice(self, text, filename):
        """Generate calming speech from text"""
        engine = pyttsx3.init()
        self._configure_voice(engine)
        
        output_path = os.path.join(self.audio_dir, f'{filename}.wav')
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        return output_path
    
    def _configure_voice(self, engine):
        """Set optimal voice parameters"""
        voices = engine.getProperty('voices')
        
        # Prefer calming female voices
        preferred_voices = [
            'Microsoft Zira Desktop',
            'Microsoft Hazel Desktop',
            'VW Julie',
            'VW Kate'
        ]
        
        for voice in voices:
            if any(pref in voice.name for pref in preferred_voices):
                engine.setProperty('voice', voice.id)
                break
        
        # Calming speech parameters
        engine.setProperty('rate', 140)  # Slightly slower
        engine.setProperty('volume', 0.8)  # Not too loud
        engine.setProperty('pitch', 0.9)  # Slightly lower pitch

class AudioPlayer:
    def __init__(self):
        self.audio_dir = os.path.join(os.path.dirname(__file__), 'Audio_Files')
    
    def play_audio(self, filename):
        """Play generated audio file"""
        filepath = os.path.join(self.audio_dir, filename)
        if os.path.exists(filepath):
            # Platform-independent playback
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(filepath)
                else:  # Mac/Linux
                    subprocess.call(['afplay' if sys.platform == 'darwin' else 'aplay', filepath])
            except Exception as e:
                print(f"Error playing audio: {e}")

class AudioSystem(AudioGenerator, AudioPlayer):
    def __init__(self):
        AudioGenerator.__init__(self)
        AudioPlayer.__init__(self)
    
    def speak(self, text, delete_after=True):
        """Generate and immediately play audio"""
        filename = f"temp_{int(time.time())}"
        audio_file = self.generate_soothing_voice(text, filename)
        self.play_audio(audio_file)
        
        if delete_after:
            time.sleep(1)  # Ensure playback completes
            try:
                os.remove(audio_file)
            except:
                pass