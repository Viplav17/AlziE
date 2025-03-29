import csv
import random
import os
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import pygame
from pygame import mixer
import json
import time
import re
from collections import defaultdict

# Configuration
CSV_FILE = 'Patient_Data.csv'
MUSIC_FOLDER = 'Music'
SESSION_LOG = 'session_log.json'

class MusicPlayer:
    def __init__(self):
        pygame.init()
        mixer.init()
        self.current_track = None
        self.volume = 0.5
        self.load_music_files()
    
    def load_music_files(self):
        if not os.path.exists(MUSIC_FOLDER):
            os.makedirs(MUSIC_FOLDER)
            print(f"Created music directory at {MUSIC_FOLDER}")
        self.music_files = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith('.mp3')]
        print(f"Found {len(self.music_files)} music files")
    
    def play_music(self, track_num=None):
        if not self.music_files:
            print("No music files available")
            return False
        try:
            if track_num:
                track = f"{MUSIC_FOLDER}/File{track_num}.mp3"
                if not os.path.exists(track):
                    print(f"Track {track_num} not found")
                    return False
            else:
                track = os.path.join(MUSIC_FOLDER, random.choice(self.music_files))
            
            print(f"Playing track: {track}")
            mixer.music.load(track)
            mixer.music.set_volume(self.volume)
            mixer.music.play()
            self.current_track = track
            return True
        except Exception as e:
            print(f"Error playing music: {e}")
            return False
    
    def stop_music(self):
        mixer.music.stop()
        self.current_track = None
    
    def set_volume(self, level):
        self.volume = max(0, min(1, level))
        mixer.music.set_volume(self.volume)
    
    def is_playing(self):
        return mixer.music.get_busy()

class VoiceInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        
        # Configure voice properties
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)
        
        # Try to find a female voice
        for voice in voices:
            if 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def listen(self):
        with self.microphone as source:
            print("\nListening... (speak now)")
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Recognized: {text}")
                return text
            except sr.WaitTimeoutError:
                print("Listening timeout - no speech detected")
                return None
            except sr.UnknownValueError:
                print("Could not understand speech")
                return None
            except Exception as e:
                print(f"Voice recognition error: {e}")
                return None
    
    def speak(self, text):
        print(f"AlziE: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Speech synthesis error: {e}")

class MoodAnalyzer:
    def __init__(self):
        self.mood_history = defaultdict(list)
        self.current_mood = "neutral"
        self.stress_level = 0
    
    def analyze_text(self, text):
        if not text:
            return self.current_mood
            
        positive_words = ['happy','good','great','wonderful','joy','excited','fantastic','perfect','amazing','calm']
        negative_words = ['sad','angry','upset','scared','afraid','depressed','anxious','worried','frustrated','lost','confused']
        urgent_words = ['help','emergency','danger','pain','hurt','fall','bleeding']
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in urgent_words):
            self.current_mood = "urgent"
            self.stress_level = min(10, self.stress_level + 3)
        elif any(word in text_lower for word in positive_words):
            self.current_mood = "positive"
            self.stress_level = max(0, self.stress_level - 1)
        elif any(word in text_lower for word in negative_words):
            self.current_mood = "negative"
            self.stress_level = min(10, self.stress_level + 2)
        else:
            self.current_mood = "neutral"
            
        print(f"Mood analysis: {self.current_mood}, Stress: {self.stress_level}")
        return self.current_mood
    
    def get_suggested_intervention(self, patient_data):
        if self.stress_level > 7:
            return "emergency_contact"
        elif self.stress_level > 5:
            return random.choice(["music", "family_reassurance", "comfort_object"])
        elif self.stress_level > 3:
            return random.choice(["breathing_exercise", "favorite_activity"])
        return "none"
    
    def reset_stress(self):
        self.stress_level = max(0, self.stress_level - 1)

class PatientDatabase:
    def __init__(self):
        self.patients = {}
        self.current_patient = None
        self._initialize_patient_data()
    
    def _initialize_patient_data(self):
        try:
            if not os.path.exists(CSV_FILE):
                print(f"Patient data file not found, creating sample data at {CSV_FILE}")
                self._create_sample_data()
            
            if os.path.getsize(CSV_FILE) == 0:
                print("Patient data file is empty, recreating...")
                self._create_sample_data()
            
            self._load_patient_data()
            
            if not self.patients:
                print("No patients loaded, creating sample data...")
                self._create_sample_data()
                self._load_patient_data()
                
        except Exception as e:
            print(f"Error initializing patient data: {e}")
            self._create_sample_data()
            self._load_patient_data()
    
    def _load_patient_data(self):
        try:
            with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    raise ValueError("CSV file has no headers")
                
                self.patients = {}
                for row in reader:
                    if 'patient_id' not in row:
                        continue
                    self.patients[row['patient_id']] = row
                
                print(f"Loaded {len(self.patients)} patients")
        except Exception as e:
            print(f"Error loading patient data: {e}")
            raise
    
    def _create_sample_data(self):
        sample_data = [{
            'patient_id': 'SM1001',
            'first_name': 'Saksham',
            'last_name': 'Malhotra',
            'age': '28',
            'address': '123 Wellness Lane',
            'city': 'Health City',
            'emergency_contact1': 'Naveen Malhotra',
            'emergency_relation1': 'Father',
            'emergency_phone1': '+1 (555) 987-6543',
            'music_preference': 'Classical',
            'hobby1': 'Reading',
            'hobby2': 'Photography',
            'hobby3': 'Chess',
            'favorite_food1': 'Butter Chicken',
            'favorite_food2': 'Palak Paneer',
            'favorite_food3': 'Biryani',
            'father_name': 'Naveen',
            'mother_name': 'Renu',
            'comfort_items': 'blanket, photo album',
            'preserved_memories': 'college graduation, first job, wedding day',
            'cognitive_strengths': 'remembering names, recognizing faces',
            'exercise_type': 'Swimming, Yoga',
            'daily_routine': 'morning walk, afternoon tea, evening music',
            'blood_pressure': '120/80',
            'resting_heart_rate': '72',
            'glucose_level': '99',
            'cholesterol_level': '150',
            'current_medications': 'Multivitamin, Omega-3'
        }]
        
        try:
            os.makedirs(os.path.dirname(CSV_FILE) or '.', exist_ok=True)
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
                writer.writeheader()
                writer.writerows(sample_data)
            print("Sample patient data created")
        except Exception as e:
            print(f"Error creating sample data: {e}")
            raise
    
    def get_patient(self, patient_id):
        try:
            if not self.patients:
                print("No patient data available")
                return False
            
            self.current_patient = self.patients.get(patient_id)
            if not self.current_patient:
                print(f"Patient {patient_id} not found")
                return False
            
            required_fields = ['first_name', 'last_name', 'age', 'emergency_contact1', 'emergency_phone1']
            for field in required_fields:
                if field not in self.current_patient:
                    print(f"Missing required field: {field}")
                    return False
            
            print(f"Loaded patient {patient_id}")
            return True
            
        except Exception as e:
            print(f"Error getting patient: {e}")
            return False
    
    def get_patient_summary(self):
        if not self.current_patient:
            return ""
        return (f"{self.current_patient['first_name']} {self.current_patient['last_name']}, age {self.current_patient['age']}. "
                f"Emergency contact: {self.current_patient['emergency_contact1']} "
                f"({self.current_patient['emergency_relation1']}) at {self.current_patient['emergency_phone1']}")

class ResponseEngine:
    def __init__(self, patient_db, voice_interface, music_player):
        self.db = patient_db
        self.voice = voice_interface
        self.music = music_player
        self.mood_analyzer = MoodAnalyzer()
        self.orientation_helper = OrientationHelper(patient_db)
        self.response_log = []
        
        self.templates = {
            'greeting': [
                "Hello there, it's good to see you today",
                "Good {time}, how are you feeling?",
                "Welcome back! What shall we do today?",
                "Lovely to connect with you again"
            ],
            'memory': [
                "Do you remember when you used to {activity}? Those were wonderful times",
                "Tell me about {memory}",
                "Let's reminisce about {memory} together"
            ],
            'comfort': [
                "It's okay, would your {item} help you feel better?",
                "Let's get your {item}, that might help",
                "Remember your {item}? It always brings comfort"
            ],
            'activity': [
                "Would you like to {activity} now?",
                "How about some {activity}? It might be enjoyable",
                "Your favorite {activity} would be perfect right now"
            ],
            'music': [
                "Let's play some music for you",
                "How about some nice music to lift your spirits?",
                "Would you like me to play some {music_preference}?"
            ],
            'emergency': [
                "I can contact {contact} for you. Would you like me to call them?",
                "Your emergency contact {contact} can help. Want me to dial them?"
            ],
            'default': [
                "I'm here with you",
                "What would you like to do?",
                "How can I assist you today?"
            ]
        }
    
    def generate_response(self, input_text):
        if not input_text:
            return random.choice(["I didn't hear that clearly", "Could you please repeat that?"])
            
        if not self.db.current_patient:
            return "Please select a patient first"
            
        patient = self.db.current_patient
        name = patient.get('first_name', 'friend')
        mood = self.mood_analyzer.analyze_text(input_text)
        
        # Handle common queries
        if any(word in input_text for word in ['who am i', 'my name', 'what is my name']):
            return (f"You are {patient['first_name']} {patient['last_name']}, "
                   f"a {patient['age']} year old. You live at {patient.get('address', 'your home')}.")
        
        if any(word in input_text for word in ['where am i', 'what is this place', 'location']):
            return f"You're at {patient.get('address', 'your home')} in {patient.get('city', 'your city')}."
        
        if any(word in input_text for word in ['who are you', 'what are you']):
            return "I'm AlziE, your personal care assistant. I'm here to help and support you."
        
        # Emergency situations
        if any(word in input_text for word in ['call', 'contact', 'emergency', 'help me']) or mood == "urgent":
            contact = f"{patient['emergency_contact1']} ({patient['emergency_relation1']})"
            return random.choice(self.templates['emergency']).format(contact=contact)
        
        # Mood-based responses
        intervention = self.mood_analyzer.get_suggested_intervention(patient)
        if intervention == "emergency_contact":
            contact = f"{patient['emergency_contact1']} ({patient['emergency_relation1']})"
            return f"You seem very stressed. {random.choice(self.templates['emergency']).format(contact=contact)}"
        elif intervention == "music":
            if self.music.play_music():
                return random.choice(self.templates['music']).format(
                    music_preference=patient.get('music_preference', 'music'))
            return "Let's take some deep breaths together."
        elif intervention == "family_reassurance":
            family_member = random.choice([patient.get('father_name', 'father'), 
                                         patient.get('mother_name', 'mother')])
            return f"Would you like to talk about {family_member}?"
        
        # Music control
        if any(word in input_text for word in ['play music', 'some music', 'listen to']):
            if self.music.play_music():
                return random.choice(self.templates['music']).format(
                    music_preference=patient.get('music_preference', 'music'))
            return "I couldn't find any music to play."
        
        if any(word in input_text for word in ['stop music', 'quiet', 'turn off']):
            self.music.stop_music()
            return "The music has been stopped."
        
        # Greeting
        if any(word in input_text for word in ['hello', 'hi', 'good morning', 'good afternoon']):
            return random.choice(self.templates['greeting']).format(
                time=self._get_time_of_day())
        
        # Default response
        if random.random() < 0.3:
            return random.choice([f"{name}, I'm here with you", 
                               f"What would you like to do, {name}?"])
        return random.choice(self.templates['default'])
    
    def _get_time_of_day(self):
        hour = datetime.now().hour
        if hour < 12: return 'morning'
        elif hour < 17: return 'afternoon'
        else: return 'evening'

class OrientationHelper:
    def __init__(self, patient_db):
        self.db = patient_db
        self.last_orientation_time = 0
    
    def should_remind(self):
        return time.time() - self.last_orientation_time > 3600
    
    def update_reminder_time(self):
        self.last_orientation_time = time.time()

class SessionLogger:
    def __init__(self):
        self.session_data = {
            'start_time': datetime.now().isoformat(),
            'interactions': [],
            'end_time': None
        }
    
    def log_interaction(self, user_input, system_response):
        self.session_data['interactions'].append({
            'timestamp': datetime.now().isoformat(),
            'input': user_input,
            'response': system_response
        })
    
    def save_session(self):
        self.session_data['end_time'] = datetime.now().isoformat()
        try:
            with open(SESSION_LOG, 'a') as f:
                json.dump(self.session_data, f)
                f.write('\n')
            print("Session saved successfully")
        except Exception as e:
            print(f"Error saving session: {e}")

def simulate_conversation():
    print("Initializing AlziE system...")
    
    try:
        # Initialize components
        db = PatientDatabase()
        if not db.get_patient('SM1001'):
            return "Error: Could not load patient data"
        
        voice = VoiceInterface()
        music_player = MusicPlayer()
        engine = ResponseEngine(db, voice, music_player)
        logger = SessionLogger()
        
        print("System ready. Starting conversation...")
        voice.speak("Welcome to AlziE. I'm ready to assist you.")
        
        while True:
            try:
                print("\nListening... (say 'goodbye' to exit)")
                user_input = voice.listen()
                
                if user_input is None:
                    continue
                
                if any(word in user_input for word in ['goodbye', 'quit', 'exit', 'bye']):
                    voice.speak("Goodbye for now. Remember, I'm always here when you need me.")
                    break
                
                response = engine.generate_response(user_input)
                logger.log_interaction(user_input, response)
                voice.speak(response)
                
            except KeyboardInterrupt:
                voice.speak("Goodbye. Have a peaceful day.")
                break
            except Exception as e:
                print(f"Conversation error: {e}")
                voice.speak("Let's try that again. Could you please repeat what you said?")
        
        logger.save_session()
        print("\nConversation ended.")
        
    except Exception as e:
        print(f"System error: {e}")
        return "System initialization failed"

if __name__ == "__main__":
    simulate_conversation()