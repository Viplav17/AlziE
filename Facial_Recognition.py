import cv2
import numpy as np
import os
import math
import time  # Import time module for delay
from typing import Tuple, Union

# Constants for drawing bounding boxes
MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # red

# Load pictures from the directory (assuming they are stored as 101.jpg, 102.jpg, etc.)
def load_known_images(image_folder="Picture_Source"):
    known_images = []
    labels = []
    for image_id in range(101, 106):  # Assuming image ids are 101 to 105
        image_path = os.path.join(image_folder, f"{image_id}.jpg")
        if os.path.exists(image_path):
            image = cv2.imread(image_path)
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            known_images.append(gray_image)
            labels.append(image_id)
    return known_images, labels

# Function to train the face recognizer
def train_face_recognizer(known_images, labels):
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.train(known_images, np.array(labels))
    return face_recognizer

# Simple distance estimation function based on face size
def estimate_distance(face_width):
    # Simple inverse relation (more the width, closer the person)
    # This is a rough approximation
    focal_length = 1000  # Example constant, you may need to calibrate it
    known_width = 150  # Average width of face in real life (in mm)
    distance = (focal_length * known_width) / face_width
    return distance

# Initialize webcam
cap = cv2.VideoCapture(0)

# Load the known images (101-105)
known_images, labels = load_known_images()
face_recognizer = train_face_recognizer(known_images, labels)

# Use OpenCV's pre-trained face detection classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

last_print_time = 0  # Variable to track the last print time
delay = 3  # 3 seconds delay

while True:
    # Capture frame-by-frame from webcam
    ret, frame = cap.read()

    if not ret:
        break

    # Convert to grayscale for face recognition
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        face_roi = gray_frame[y:y + h, x:x + w]

        # Predict the ID using the trained face recognizer
        recognized_id, confidence = face_recognizer.predict(face_roi)

        # Estimate the distance based on the face width
        distance = estimate_distance(w)

        # Continuously display the ID and distance on the frame
        if recognized_id is not None:
            cv2.putText(frame, f"ID: {recognized_id}, Distance: {distance:.2f} cm", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Check if it's time to print to the terminal (every 3 seconds)
        current_time = time.time()
        if current_time - last_print_time >= delay:  # Check if 3 seconds have passed
            # Print ID and distance to the terminal
            if recognized_id is not None:
                print(f"ID: {recognized_id}, Distance: {distance:.2f} cm")  # Print ID and distance in cm
                last_print_time = current_time  # Update the last print time

        # Draw rectangle around the detected face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Display the resulting frame
    cv2.imshow('Webcam Feed', frame)

    # Break the loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
