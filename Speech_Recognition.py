import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Function to listen to the microphone and recognize speech continuously
def recognize_speech():
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise levels
        print("Listening... Speak now!")
        
        try:
            while True:  # Keep listening indefinitely
                audio = recognizer.listen(source)
                print("Recognizing...")
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
        
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        

# Main function to start continuous speech recognition
def main():
    print("Continuous Speech Recognition Initialized.")
    text = recognize_speech()
    return text


if __name__ == "__main__":
    main()


