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
            for i in range(1, 6):
                open(f"{MUSIC_FOLDER}/File{i}.mp3", 'a').close()
        self.music_files = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith('.mp3')]
    
    def play_music(self, track_num=None):
        if not self.music_files:
            return False
        try:
            track = f"{MUSIC_FOLDER}/File{track_num}.mp3" if track_num else random.choice(self.music_files)
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
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voices', 1)
        self.engine.setProperty('rate', 130)
        self.engine.setProperty('volume', 1.0)
        for voice in voices:
            if 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def listen(self):
        with self.microphone as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=8)
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                print("Listening timed out")
                return ""
            except sr.UnknownValueError:
                print("Could not understand audio")
                return ""
            except Exception as e:
                print(f"Error in voice recognition: {e}")
                return ""
    
    def speak(self, text):
        print(f"AlziE: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def slow_speak(self, text, pause=0.1):
        for sentence in re.split(r'[.!?]', text):
            if sentence.strip():
                self.engine.say(sentence.strip())
                self.engine.runAndWait()
                time.sleep(pause)

class MoodAnalyzer:
    def __init__(self):
        self.mood_history = defaultdict(list)
        self.current_mood = "neutral"
        self.stress_level = 0
    
    def analyze_text(self, text):
        positive_words = ['happy','good','great','wonderful','joy','excited','fantastic','perfect','amazing','calm']
        negative_words = ['sad','angry','upset','scared','afraid','depressed','anxious','worried','frustrated','lost','confused']
        urgent_words = ['help','emergency','danger','pain','hurt','fall','bleeding']
        
        if any(word in text for word in urgent_words):
            self.current_mood = "urgent"
            self.stress_level = min(10, self.stress_level + 3)
        elif any(word in text for word in positive_words):
            self.current_mood = "positive"
            self.stress_level = max(0, self.stress_level - 1)
        elif any(word in text for word in negative_words):
            self.current_mood = "negative"
            self.stress_level = min(10, self.stress_level + 2)
        else:
            self.current_mood = "neutral"
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

class HealthMonitor:
    def __init__(self):
        self.vitals_history = defaultdict(list)
        self.medication_times = {}
    
    def check_vitals(self, patient_data):
        bp = patient_data.get('blood_pressure','120/80').split('/')
        systolic = int(bp[0])
        diastolic = int(bp[1])
        hr = int(patient_data.get('resting_heart_rate',72))
        glucose = int(patient_data.get('glucose_level',99))
        cholesterol = int(patient_data.get('cholesterol_level',150))
        alerts = []
        if systolic > 140 or diastolic > 90:
            alerts.append("high blood pressure")
        if hr > 100:
            alerts.append("elevated heart rate")
        if glucose > 126:
            alerts.append("high glucose level")
        if cholesterol > 200:
            alerts.append("high cholesterol")
        return alerts
    
    def check_medication_time(self, patient_data):
        meds = patient_data.get('current_medications','').split(',')
        for med in meds:
            if med.strip() not in self.medication_times:
                self.medication_times[med.strip()] = time.time() + random.randint(3600, 7200)
        reminders = []
        current_time = time.time()
        for med, next_time in self.medication_times.items():
            if current_time > next_time:
                reminders.append(med)
                self.medication_times[med] = current_time + random.randint(3600, 7200)
        return reminders

class PatientDatabase:
    def __init__(self):
        self.patients = {}
        self.current_patient = None
        self._initialize_patient_data()
    
    def _initialize_patient_data(self):
        """Initialize patient data with comprehensive error handling"""
        try:
            if not os.path.exists(CSV_FILE):
                print(f"Patient data file not found at {CSV_FILE}, creating sample data...")
                self._create_sample_data()
            
            # Verify file is not empty
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
        """Load patient data from CSV with validation"""
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
                
                print(f"Successfully loaded {len(self.patients)} patients")
        except Exception as e:
            print(f"Error loading patient data: {e}")
            raise
    
    def _create_sample_data(self):
        """Generate comprehensive sample patient data"""
        print("Creating sample patient data...")
        sample_data = [{
            'patient_id': 'SM1001',
            'first_name': 'Saksham',
            'last_name': 'Malhotra',
            'date_of_birth': '1995-08-15',
            'age': '28',
            'gender': 'Male',
            'height_cm': '175',
            'weight_kg': '70',
            'bmi': '22.86',
            'blood_type': 'A+',
            'primary_language': 'Hindi',
            'secondary_language': 'English',
            'father_name': 'Naveen Malhotra',
            'mother_name': 'Renu Malhotra',
            'address': '123 Wellness Lane',
            'city': 'Health City',
            'state': 'CA',
            'zip_code': '90210',
            'country': 'USA',
            'primary_phone': '+1 (555) 123-4567',
            'secondary_phone': '+1 (555) 111-2222',
            'personal_email': 'saksham.m@email.com',
            'emergency_contact1': 'Naveen Malhotra',
            'emergency_relation1': 'Father',
            'emergency_phone1': '+1 (555) 987-6543',
            'emergency_contact2': 'Dr. Amit Sharma',
            'emergency_relation2': 'Physician',
            'emergency_phone2': '+1 (555) 456-7890',
            'primary_care_physician': 'Renu Malhotra',
            'physician_phone': '+1 (555) 789-0123',
            'insurance_provider': 'HealthPlus Insurance',
            'policy_number': 'HPI-2023-SM1001',
            'allergies': 'None',
            'current_medications': 'Multivitamin, Omega-3',
            'medical_history': 'Asthma (childhood)',
            'surgical_history': 'None',
            'family_history': 'Diabetes (paternal)',
            'typical_sleep_hours': '7.5',
            'sleep_quality': 'Good',
            'exercise_frequency': '4/week',
            'exercise_type': 'Swimming, Yoga',
            'diet_type': 'Mediterranean',
            'vegetarian': 'No',
            'vegan': 'No',
            'gluten_free': 'No',
            'dairy_free': 'No',
            'favorite_food1': 'Butter Chicken',
            'favorite_food2': 'Palak Paneer',
            'favorite_food3': 'Biryani',
            'food_aversions': 'Raw onions, Mushrooms',
            'daily_water_intake_ml': '2500',
            'daily_caffeine_intake': 'Moderate',
            'daily_tea_cups': '3',
            'preferred_tea_type': 'Assam',
            'coffee_preference': 'None',
            'alcohol_consumption': 'Occasional',
            'smoking_status': 'Never',
            'substance_use': 'None',
            'hobby1': 'Reading',
            'hobby2': 'Photography',
            'hobby3': 'Chess',
            'music_preference': 'Classical',
            'reading_frequency': 'Weekly',
            'reading_genre': 'Fiction',
            'travel_frequency': '2/year',
            'pet_ownership': 'Yes',
            'pet_type': 'Dog',
            'marital_status': 'Single',
            'children': 'None',
            'occupation': 'Software Engineer',
            'employer': 'Tech Solutions Inc',
            'work_schedule': '9am-5pm',
            'education_level': 'Masters',
            'religion': 'Hindu',
            'stress_level': 'Moderate',
            'stress_triggers': 'Work deadlines, Traffic',
            'mental_health_notes': 'Anxiety management',
            'last_physical_date': '2023-10-15',
            'next_appointment_date': '2024-01-15',
            'vaccination_status': 'Up-to-date',
            'covid_vaccine_date': '2022-03-15',
            'blood_pressure': '120/80',
            'resting_heart_rate': '68',
            'cholesterol_level': '180',
            'glucose_level': '92',
            'last_updated': '2023-11-20'
        }]
        
        try:
            os.makedirs(os.path.dirname(CSV_FILE) or os.path.dirname(CSV_FILE), exist_ok=True)
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
                writer.writeheader()
                writer.writerows(sample_data)
            print("Sample patient data created successfully")
        except Exception as e:
            print(f"Error creating sample data: {e}")
            raise
    
    def get_patient(self, patient_id):
        """Retrieve patient with comprehensive validation"""
        try:
            if not self.patients:
                print("No patient data available")
                return False
            
            self.current_patient = self.patients.get(patient_id)
            if not self.current_patient:
                print(f"Patient {patient_id} not found")
                return False
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'age', 'emergency_contact1', 'emergency_phone1']
            for field in required_fields:
                if field not in self.current_patient:
                    print(f"Missing required field: {field}")
                    return False
            
            print(f"Successfully loaded patient {patient_id}")
            return True
            
        except Exception as e:
            print(f"Error getting patient: {e}")
            return False
    
    def get_patient_summary(self):
        """Generate comprehensive patient summary"""
        if not self.current_patient:
            return ""
        return (f"{self.current_patient['first_name']} {self.current_patient['last_name']}, age {self.current_patient['age']}. "
                f"Address: {self.current_patient['address']}, {self.current_patient['city']}. "
                f"Emergency contact: {self.current_patient['emergency_contact1']} "
                f"({self.current_patient['emergency_relation1']}) at {self.current_patient['emergency_phone1']}")

class OrientationHelper:
    def __init__(self, patient_db):
        self.db = patient_db
        self.last_orientation_time = 0
    
    def get_orientation_info(self):
        """Generate complete orientation information"""
        patient = self.db.current_patient
        if not patient:
            return {}
        
        now = datetime.now()
        return {
            'time': now.strftime("%I:%M %p on %A, %B %d"),
            'location': f"{patient['address']}, {patient['city']}, {patient['state']}",
            'person': f"You are {patient['first_name']} {patient['last_name']}, a {patient['age']} year old {patient['occupation']}",
            'emergency_info': f"Your emergency contact is {patient['emergency_contact1']} ({patient['emergency_relation1']}) at {patient['emergency_phone1']}"
        }
    
    def should_remind(self):
        """Determine if orientation reminder is needed"""
        return time.time() - self.last_orientation_time > 3600  # 1 hour
    
    def update_reminder_time(self):
        """Update last reminder time"""
        self.last_orientation_time = time.time()

class ResponseEngine:
    def __init__(self, patient_db, voice_interface, music_player):
        self.db = patient_db
        self.voice = voice_interface
        self.music = music_player
        self.mood_analyzer = MoodAnalyzer()
        self.health_monitor = HealthMonitor()
        self.orientation_helper = OrientationHelper(patient_db)
        self.response_log = []
        self.last_used_name = None
        self.final_response = ""
        self.patient_summary = patient_db.get_patient_summary()
        
        # Enhanced response templates with Alzheimer's-specific additions
        self.templates = {
            'greeting': [
                "Hello there, it's good to see you today",
                "Good {time}, how are you feeling?",
                "Welcome back, my friend! What shall we do today?",
                "Lovely to connect with you again",
                "What a pleasant {time} we're having"
            ],
            'memory': [
                "Do you remember when you used to {activity}? Those were wonderful times",
                "Tell me about {memory}",
                "I know you remember {strength} well",
                "Let's reminisce about {memory} together",
                "Your memory of {memory} is quite special"
            ],
            'comfort': [
                "It's okay, would your {item} help you feel better?",
                "Let's get your {item}, that might help",
                "Remember your {item}? It always brings comfort",
                "Would holding your {item} make you feel more at ease?",
                "Your {item} is nearby if you need it"
            ],
            'activity': [
                "Would you like to {activity} now?",
                "This might be a good time for {activity}",
                "How about some {activity}? It might be enjoyable",
                "I recall you enjoy {activity}. Shall we do that?",
                "Your favorite {activity} would be perfect right now"
            ],
            'time_based': [
                "It's {current_time}, time for your {routine}",
                "According to your routine, it's time for {routine}",
                "Shall we prepare for {routine}? It's that time",
                "Your schedule shows {routine} should happen now",
                "{routine} time is approaching"
            ],
            'food': [
                "I remember you enjoy {food}. Would you like some now?",
                "How about some {food}? It's one of your favorites",
                "You haven't had {food} in a while. Would you like some?",
                "{food} sounds delicious right about now, doesn't it?",
                "Your favorite {food} is available if you're interested"
            ],
            'family': [
                "Would you like to talk about {family_member}?",
                "I remember you mentioning {family_member} recently",
                "How is {family_member} doing these days?",
                "Thinking about {family_member} might bring you joy",
                "Would you like to call {family_member}?"
            ],
            'reassurance': [
                "Everything is alright, I'm here with you",
                "You're safe here, don't worry",
                "I'll stay right here with you",
                "This moment will pass, I'm with you",
                "Take deep breaths, I'm right here"
            ],
            'music': [
                "Let's play some music for you",
                "How about some nice music to lift your spirits?",
                "Music can be comforting. Shall we listen to something?",
                "Your favorite music is ready to play",
                "Would you like me to play some {music_preference}?"
            ],
            'health': [
                "I notice your {vital} is slightly elevated",
                "Your recent {vital} reading deserves attention",
                "Shall we discuss your {vital} with your doctor?",
                "Your health report shows {vital} needs monitoring",
                "Let's keep an eye on your {vital}"
            ],
            'hobby': [
                "Would you like to work on {hobby} today?",
                "How about some {hobby} to pass the time?",
                "Your {hobby} materials are ready if you're interested",
                "Engaging in {hobby} might be enjoyable now",
                "I remember you find {hobby} relaxing"
            ],
            'pet': [
                "Would you like to spend time with your {pet}?",
                "Your {pet} is waiting for your attention",
                "Playing with your {pet} might be fun",
                "How about taking your {pet} for a walk?",
                "Your {pet} always cheers you up"
            ],
            'work': [
                "Would you like to talk about your work at {employer}?",
                "How was your day at {occupation}?",
                "Your work as {occupation} is quite impressive",
                "Would you like to discuss your work schedule?",
                "How are things going at {employer}?"
            ],
            'orientation': [
                "Let me remind you: {orientation_info}",
                "Here's what you should know: {orientation_info}",
                "To help you remember: {orientation_info}",
                "Just to orient you: {orientation_info}",
                "Let me tell you about yourself: {orientation_info}"
            ],
            'identity': [
                "You are {name}, {age} years old. You live at {location}",
                "Your name is {name}, you're {age} years young! You're currently at {location}",
                "Let me remind you - you're {name}, aged {age}, residing at {location}",
                "I know you as {name}, {age} years old, living at {location}",
                "You go by {name}, you've lived {age} wonderful years, and your home is at {location}"
            ],
            'location': [
                "You're at {location} right now",
                "Currently you're located at {location}",
                "Your present location is {location}",
                "You're safe at {location}",
                "This is {location}, where you live"
            ],
            'emergency': [
                "I can contact {contact} for you. Would you like me to call them?",
                "Let me reach out to {contact} for assistance. Should I call?",
                "Your emergency contact {contact} can help. Want me to dial them?",
                "I'll connect you with {contact} if you'd like",
                "{contact} is available to help. Shall I call them?"
            ],
            'breathing': [
                "Let's do a calming exercise. Breathe in... hold... and out. Repeat with me",
                "Follow my breathing: In... 2... 3... 4... Hold... 2... 3... Out... 2... 3... 4...",
                "Try this breathing pattern with me: inhale deeply, hold, exhale slowly",
                "Let's practice deep breathing together. Ready? In... and out...",
                "Breathing can help. Inhale deeply through your nose, exhale through your mouth"
            ],
            'default': [
                "I'm here with you",
                "What would you like to do?",
                "Let me know how I can help",
                "I'm listening",
                "How can I assist you today?"
            ]
        }
    
    def generate_response(self, input_text):
        """Generate comprehensive response with Alzheimer's support"""
        if not self.db.current_patient:
            self.final_response = "Please select a patient first"
            return self.final_response
            
        patient = self.db.current_patient
        name = patient.get('first_name', 'friend')
        mood = self.mood_analyzer.analyze_text(input_text)
        health_alerts = self.health_monitor.check_vitals(patient)
        med_reminders = self.health_monitor.check_medication_time(patient)
        
        # Orientation reminders
        if self.orientation_helper.should_remind():
            orientation = self.orientation_helper.get_orientation_info()
            self.final_response = random.choice(self.templates['orientation']).format(
                orientation_info=f"It's {orientation['time']}. {orientation['person']}. {orientation['location']}. {orientation['emergency_info']}"
            )
            self.orientation_helper.update_reminder_time()
            return self.final_response
        
        # Alzheimer's-specific questions
        if any(word in input_text for word in ['who am i','my name','what is my name']):
            orientation = self.orientation_helper.get_orientation_info()
            self.final_response = random.choice(self.templates['identity']).format(
                name=f"{patient['first_name']} {patient['last_name']}",
                age=patient['age'],
                location=f"{patient['address']}, {patient['city']}"
            )
            return self.final_response
        
        if any(word in input_text for word in ['where am i','what is this place','location']):
            orientation = self.orientation_helper.get_orientation_info()
            self.final_response = random.choice(self.templates['location']).format(
                location=f"{patient['address']}, {patient['city']}"
            )
            return self.final_response
        
        if any(word in input_text for word in ['who are you','what are you','your name']):
            self.final_response = "I'm AlziE, your personal care assistant. I'm here to help and support you"
            return self.final_response
        
        # Emergency situations
        if any(word in input_text for word in ['call','contact','emergency','help me']) or mood == "urgent":
            contact = f"{patient['emergency_contact1']} ({patient['emergency_relation1']})"
            self.final_response = random.choice(self.templates['emergency']).format(contact=contact)
            return self.final_response
        
        # Mood-based interventions
        intervention = self.mood_analyzer.get_suggested_intervention(patient)
        if intervention == "emergency_contact":
            contact = f"{patient['emergency_contact1']} ({patient['emergency_relation1']})"
            self.final_response = f"You seem very stressed. {random.choice(self.templates['emergency']).format(contact=contact)}"
            return self.final_response
        elif intervention == "music":
            if self.music.play_music():
                music_pref = patient.get('music_preference','music')
                self.final_response = random.choice(self.templates['music']).format(music_preference=music_pref)
            else:
                self.final_response = random.choice(self.templates['breathing'])
            return self.final_response
        elif intervention == "family_reassurance":
            family_member = random.choice([
                patient.get('father_name',''),
                patient.get('mother_name','')
            ])
            self.final_response = random.choice(self.templates['family']).format(family_member=family_member)
            return self.final_response
        elif intervention == "comfort_object":
            item = random.choice(patient.get('comfort_items','').split(', '))
            self.final_response = random.choice(self.templates['comfort']).format(item=item)
            return self.final_response
        elif intervention == "breathing_exercise":
            self.final_response = random.choice(self.templates['breathing'])
            return self.final_response
        elif intervention == "favorite_activity":
            activity = random.choice([
                patient.get('hobby1',''),
                patient.get('hobby2',''),
                patient.get('hobby3','')
            ])
            self.final_response = random.choice(self.templates['activity']).format(activity=activity)
            return self.final_response
        
        # Music control
        if any(word in input_text for word in ['play music','some music','listen to','music please']):
            if self.music.play_music():
                music_pref = patient.get('music_preference','music')
                self.final_response = random.choice(self.templates['music']).format(music_preference=music_pref)
            else:
                self.final_response = "I couldn't find any music to play"
            return self.final_response
        
        if any(word in input_text for word in ['stop music','quiet','turn off','no music']):
            self.music.stop_music()
            self.final_response = "The music has been stopped"
            return self.final_response
        
        if any(word in input_text for word in ['volume up','louder','increase volume']):
            self.music.set_volume(min(1, self.music.volume + 0.2))
            self.final_response = "Volume increased"
            return self.final_response
        
        if any(word in input_text for word in ['volume down','quieter','decrease volume']):
            self.music.set_volume(max(0, self.music.volume - 0.2))
            self.final_response = "Volume decreased"
            return self.final_response
        
        # Memory recall
        if any(word in input_text for word in ['remember','forgot','memory','recall']):
            memory = random.choice(patient.get('preserved_memories','').split(', '))
            strength = random.choice(patient.get('cognitive_strengths','').split(', '))
            self.final_response = random.choice(self.templates['memory']).format(
                activity=random.choice(patient.get('exercise_type','').split(', ')),
                memory=memory, strength=strength
            )
            return self.final_response
        
        # Comfort/Stress
        if any(word in input_text for word in ['scared','anxious','upset','afraid','nervous']):
            item = random.choice(patient.get('comfort_items','').split(', '))
            self.final_response = random.choice(self.templates['comfort']).format(item=item)
            return self.final_response
        
        # Activity suggestion
        if any(word in input_text for word in ['bored','do now','what to do','nothing to do','lonely']):
            activity = random.choice([
                patient.get('hobby1',''),
                patient.get('hobby2',''),
                patient.get('hobby3','')
            ])
            self.final_response = random.choice(self.templates['activity']).format(activity=activity)
            return self.final_response
        
        # Greeting
        if any(word in input_text for word in ['hello','hi','good morning','good afternoon','hey']):
            self.final_response = random.choice(self.templates['greeting']).format(
                time=self._get_time_of_day()
            )
            return self.final_response
        
        # Time-based routine
        if any(word in input_text for word in ['time','what time','schedule','appointment']):
            routine = random.choice(patient.get('daily_routine','').split(', '))
            self.final_response = random.choice(self.templates['time_based']).format(
                current_time=datetime.now().strftime("%I:%M %p"),
                routine=routine
            )
            return self.final_response
        
        # Food-related
        if any(word in input_text for word in ['hungry','food','eat','thirsty','meal']):
            food = random.choice([
                patient.get('favorite_food1',''),
                patient.get('favorite_food2',''),
                patient.get('favorite_food3','')
            ])
            self.final_response = random.choice(self.templates['food']).format(food=food)
            return self.final_response
        
        # Family-related
        if any(word in input_text for word in ['family','mother','father','son','daughter','parents']):
            family_member = random.choice([
                patient.get('father_name',''),
                patient.get('mother_name','')
            ])
            self.final_response = random.choice(self.templates['family']).format(family_member=family_member)
            return self.final_response
        
        # Reassurance
        if any(word in input_text for word in ['help','scared','lost','confused','anxiety']):
            self.final_response = random.choice(self.templates['reassurance'])
            return self.final_response
        
        # Health monitoring
        if any(word in input_text for word in ['health','vitals','blood pressure','heart rate']):
            if health_alerts:
                vital = random.choice(health_alerts)
                self.final_response = random.choice(self.templates['health']).format(vital=vital)
            else:
                self.final_response = "Your vital signs appear normal"
            return self.final_response
        
        # Hobbies
        if any(word in input_text for word in ['hobby','chess','read','photography']):
            hobby = random.choice([
                patient.get('hobby1',''),
                patient.get('hobby2',''),
                patient.get('hobby3','')
            ])
            self.final_response = random.choice(self.templates['hobby']).format(hobby=hobby)
            return self.final_response
        
        # Pets
        if any(word in input_text for word in ['pet','dog','animal','companion']):
            if patient.get('pet_ownership','').lower() == 'yes':
                pet_type = patient.get('pet_type','pet')
                self.final_response = random.choice(self.templates['pet']).format(pet=pet_type)
            else:
                self.final_response = "Would you like to talk about animals?"
            return self.final_response
        
        # Work
        if any(word in input_text for word in ['work','job','employer','office']):
            employer = patient.get('employer','work')
            occupation = patient.get('occupation','job')
            self.final_response = random.choice(self.templates['work']).format(
                employer=employer,
                occupation=occupation
            )
            return self.final_response
        
        # Medication reminders
        if med_reminders:
            self.final_response = f"Remember to take your {', '.join(med_reminders)}"
            return self.final_response
        
        # Default response with occasional name usage
        if random.random() < 0.3:
            self.final_response = random.choice([
                f"{name}, I'm here with you",
                f"What would you like to do, {name}?",
                f"Let me know how I can help, {name}"
            ])
        else:
            self.final_response = random.choice(self.templates['default'])
        return self.final_response
    
    def _get_time_of_day(self):
        hour = datetime.now().hour
        if hour < 12: return 'morning'
        elif hour < 17: return 'afternoon'
        else: return 'evening'

class SessionLogger:
    def __init__(self):
        self.session_data = {
            'start_time': datetime.now().isoformat(),
            'interactions': [],
            'end_time': None,
            'stress_levels': [],
            'interventions': [],
            'orientation_reminders': 0
        }
    
    def log_interaction(self, user_input, system_response, mood_analyzer):
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'input': user_input,
            'response': system_response,
            'mood': mood_analyzer.current_mood,
            'stress_level': mood_analyzer.stress_level
        }
        self.session_data['interactions'].append(interaction)
        self.session_data['stress_levels'].append(mood_analyzer.stress_level)
        
        if "emergency" in system_response.lower():
            self.session_data['interventions'].append("emergency_contact_suggested")
        elif "music" in system_response.lower() and "play" in system_response.lower():
            self.session_data['interventions'].append("music_played")
        elif "breathe" in system_response.lower():
            self.session_data['interventions'].append("breathing_exercise")
        elif "remind" in system_response.lower():
            self.session_data['orientation_reminders'] += 1
    
    def save_session(self):
        self.session_data['end_time'] = datetime.now().isoformat()
        try:
            with open(SESSION_LOG, 'a') as f:
                json.dump(self.session_data, f)
                f.write('\n')
            print("Session data saved successfully")
        except Exception as e:
            print(f"Error saving session data: {e}")
    
    def get_session_summary(self):
        if not self.session_data['interactions']:
            return "No interactions recorded"
        
        duration = datetime.fromisoformat(self.session_data['end_time']) - datetime.fromisoformat(self.session_data['start_time'])
        stress_avg = sum(self.session_data['stress_levels'])/len(self.session_data['stress_levels'])
        
        return (f"Session duration: {duration}. "
                f"Interactions: {len(self.session_data['interactions'])}. "
                f"Avg stress: {stress_avg:.1f}. "
                f"Interventions: {len(self.session_data['interventions'])}. "
                f"Orientation reminders: {self.session_data['orientation_reminders']}")

def simulate_conversation():
    print("Initializing AlziE system...")
    
    try:
        # Initialize all components
        db = PatientDatabase()
        if not db.get_patient('SM1001'):
            print("Critical error: Could not load patient data")
            return "System error: Could not initialize patient data"
        
        voice = VoiceInterface()
        music_player = MusicPlayer()
        engine = ResponseEngine(db, voice, music_player)
        logger = SessionLogger()
        
        print("System components initialized successfully")
        
        # Begin conversation
        final_output = ""
        final_output += "Welcome to AlziE, your personalized Alzheimer's support companion\n"
        final_output += f"Hello, I see we're with {db.current_patient['first_name']} today\n"
        final_output += "You can speak to me anytime. Say 'goodbye' when you'd like to end our conversation\n"
        
        voice.speak("Welcome to AlziE. I'm ready to assist you.")
        
        while True:
            try:
                user_input = voice.listen()
                if not user_input:
                    continue
                
                if any(word in user_input for word in ['goodbye','quit','exit','bye']):
                    final_output += "Goodbye for now. Remember, I'm always here when you need me\n"
                    voice.speak("Goodbye for now. Remember, I'm always here when you need me.")
                    break
                
                response = engine.generate_response(user_input)
                logger.log_interaction(user_input, response, engine.mood_analyzer)
                final_output += f"User: {user_input}\n"
                final_output += f"AlziE: {response}\n"
                
                voice.speak(response)
                
                # Automatic comfort measures for stressed patients
                if engine.mood_analyzer.current_mood == "negative" and not music_player.is_playing():
                    comfort_response = "I sense you might be feeling down. Would you like me to play some calming music?"
                    final_output += f"AlziE: {comfort_response}\n"
                    voice.speak(comfort_response)
                    music_player.play_music()
            
            except KeyboardInterrupt:
                final_output += "Goodbye. Have a peaceful day\n"
                voice.speak("Goodbye. Have a peaceful day.")
                break
            except Exception as e:
                error_response = "I'm sorry, I didn't quite catch that. Could you please say it again?"
                final_output += f"AlziE: {error_response}\n"
                voice.speak(error_response)
        
        # Save session and return output
        logger.save_session()
        final_output += "\nSession Summary:\n"
        final_output += logger.get_session_summary()
        
        print("\nConversation ended. Session summary:")
        print(logger.get_session_summary())
        
        return final_output
    
    except Exception as e:
        print(f"System initialization failed: {e}")
        return "System error: Initialization failed"

if __name__ == "__main__":
    result = simulate_conversation()
    print(result)