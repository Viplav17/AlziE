import os
import time
import pygame
from pygame import mixer

def play_and_delete_audio_files():
    # Initialize pygame mixer with optimal settings for voice audio
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=2048)
    
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get all WAV files in the directory, sorted by creation time
    audio_files = sorted(
        [f for f in os.listdir(current_dir) if f.lower().endswith('.wav')],
        key=lambda f: os.path.getctime(os.path.join(current_dir, f)))
    
    if not audio_files:
        print("No WAV audio files found in:", current_dir)
        return
    
    print(f"Found {len(audio_files)} audio file(s) to play:")
    
    for audio_file in audio_files:
        file_path = os.path.join(current_dir, audio_file)
        try:
            print(f"Playing: {audio_file}")
            
            # Load and play the sound
            sound = mixer.Sound(file_path)
            channel = sound.play()
            
            # Wait for playback to finish
            while channel.get_busy():
                pygame.time.Clock().tick(10)  # More efficient than sleep
                
            # Delete the file after successful playback
            os.remove(file_path)
            print(f"Deleted: {audio_file}")
            
        except pygame.error as e:
            print(f"Error playing {audio_file}: {str(e)}")
        except Exception as e:
            print(f"Error processing {audio_file}: {str(e)}")
    
    # Clean up mixer resources
    pygame.mixer.quit()
    print("Finished processing all audio files")

if __name__ == "__main__":
    try:
        play_and_delete_audio_files()
    except KeyboardInterrupt:
        print("\nPlayback interrupted by user")
    finally:
        os.exit()


