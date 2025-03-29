import pygame
import time
import os

pygame.init()
pygame.mixer.init()

MUSIC_FILE = "soothing_music.mp3"

if not os.path.exists(MUSIC_FILE):
    print(f"Error: Music file {MUSIC_FILE} not found")
    exit()

def play_comfort_music(panic_level):
    """Play music based on panic level"""
    if panic_level > 60:
        print("Playing calming music...")
        try:
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.play()
            time.sleep(30)
            pygame.mixer.music.stop()
        except pygame.error as e:
            print(f"Error playing music: {e}")
    else:
        print("Emergency situation")