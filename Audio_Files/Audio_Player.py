import os
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
