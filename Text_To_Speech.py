import pyttsx3
import os
import subprocess
import time

class AudioGenerator:
    def __init__(self):
        self.audio_dir = os.path.join(os.path.dirname(__file__), 'Audio_Files')
        self.ensure_directory_exists()
        
    def ensure_directory_exists(self):
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
    
    def generate_soothing_voice(self, text, filename):
        engine = pyttsx3.init()
        
        # Configure voice settings
        self.configure_voice(engine)
        
        # Save to file
        full_path = os.path.join(self.audio_dir, f'{filename}.wav')
        engine.save_to_file(text, full_path)
        engine.runAndWait()
        
        print(f"Generated: {full_path}")
        return full_path
    
    def configure_voice(self, engine):
        voices = engine.getProperty('voices')
        preferred_voices = [
            'Microsoft Zira Desktop',
            'Microsoft Hazel Desktop',
            'VW Julie',
            'VW Kate'
        ]
        
        for voice in voices:
            if any(pref in voice.name for pref in preferred_voices):
                engine.setProperty('voice', voice.id)
                print(f"Using voice: {voice.name}")
                break
        else:
            for voice in voices:
                if 'female' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    print(f"Using fallback voice: {voice.name}")
                    break
        
        engine.setProperty('rate', 140)
        engine.setProperty('volume', 0.8)
        engine.setProperty('pitch', 0.9)


class AudioSystem(AudioGenerator):
    def __init__(self):
        super().__init__()
        self.audio_player_path = os.path.join(self.audio_dir, 'Audio_Player.py')
    
    def create_audio_player_script(self):
        audio_player_code = """import os
import time
import pygame
from pygame import mixer

def play_and_delete_audio_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    audio_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.wav')]
    audio_files.sort()
    
    if not audio_files:
        print("No audio files found in:", current_dir)
        return
    
    for audio_file in audio_files:
        file_path = os.path.join(current_dir, audio_file)
        try:
            print(f"Loading: {audio_file}")
            sound = mixer.Sound(file_path)
            channel = sound.play()
            os.remove(file_path)
            print(f"Deleted: {audio_file}")
            while channel.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"Error processing {audio_file}: {str(e)}")
    
    print("All audio files processed.")
    pygame.mixer.quit()

if __name__ == "__main__":
    play_and_delete_audio_files()
    input("Press Enter to exit...")
"""
        with open(self.audio_player_path, 'w') as f:
            f.write(audio_player_code)
        print(f"Created audio player script at: {self.audio_player_path}")
    
    def run_audio_player(self):
        if not os.path.exists(self.audio_player_path):
            self.create_audio_player_script()
        
        # Wait a moment to ensure files are written
        time.sleep(1)
        
        # Run the audio player script
        subprocess.Popen(['python', self.audio_player_path], 
                         cwd=self.audio_dir,
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
        print("Audio player started in a new console window.")


if __name__ == "__main__":
    audio_system = AudioSystem()
    
    # Example texts to convert to speech
    texts = [
        "Hello, this is a soothing voice demonstration.",
        "Relax and enjoy the calming tone of this voice.",
        "Text to speech can be very pleasant to listen to.",
        "Thank you for using our text to speech service."
    ]
    
    # Generate audio files
    for i, text in enumerate(texts, 1):
        filename = f"soothing_voice_{i}"
        audio_system.generate_soothing_voice(text, filename)
    
    # Automatically run the audio player
    audio_system.run_audio_player()