import os
import time
import pygame
from pygame import mixer

def play_and_delete_audio_files():
    # Get the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Initialize pygame mixer with better buffer settings
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    
    # Get all WAV files in the directory
    audio_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.wav')]
    audio_files.sort()  # Play in alphabetical order
    
    if not audio_files:
        print("No audio files found in:", current_dir)
        return
    
    for audio_file in audio_files:
        file_path = os.path.join(current_dir, audio_file)
        try:
            print(f"Loading: {audio_file}")
            
            # Load and play the sound
            sound = mixer.Sound(file_path)
            channel = sound.play()
            
            # Delete the file immediately after playback starts
            os.remove(file_path)
            print(f"Deleted: {audio_file}")
            
            # Wait for playback to finish
            while channel.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error processing {audio_file}: {str(e)}")
    
    print("All audio files processed.")
    pygame.mixer.quit()

if __name__ == "__main__":
    play_and_delete_audio_files()
    input("Press Enter to exit...")