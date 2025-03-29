import pygame
import time

pygame.init()
pygame.mixer.init()

test = [10, 20, 30, 40, 50, 70]  #test percentage 

try:
    pygame.mixer.music.load("soothing_music.mp3")  # Ensure file exists!
except pygame.error as e:
    print(f"Error loading music: {e}")
    exit()

for i in test:
    if i < 0:
        print("The user is dead")
    elif i > 60:
        print("Hey, You are going to be just fine. Just listen to this.")
        pygame.mixer.music.play()
        time.sleep(30)  # Wait for 30 seconds
        pygame.mixer.music.stop()
    elif i > 30:
        continue

    else: 
        print("EMERGENCY SITUATION")

