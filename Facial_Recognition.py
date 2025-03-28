import cv2
import face_recognition
import numpy as np
import os
import threading

# Constants
TEXT_COLOR = (0, 255, 0)  # Green for recognized faces
UNKNOWN_COLOR = (0, 0, 255)  # Red for unknown faces
FONT = cv2.FONT_HERSHEY_SIMPLEX
FRAME_DOWNSCALE = 0.6  # Increase downscaling for smoother performance
FRAME_SKIP = 1  # Process every frame for real-time performance
LOCK = threading.Lock()

# Global variables for threading
face_locations = []
face_encodings = []
frame_skip_count = 0
processed_frame = None

def load_known_faces(image_folder="Picture_Source"):
    known_encodings = []
    known_labels = []

    for person_id in range(101, 106):  # Assuming IDs are from 101 to 105
        person_folder = os.path.join(image_folder, str(person_id))
        if not os.path.exists(person_folder):
            continue  # Skip if folder does not exist
        
        for image_name in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_name)

            # Read the image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                print(f"Skipping {image_path}: Unreadable format.")
                continue  # Skip unreadable images

            # Convert from BGR (OpenCV) to RGB (face_recognition uses RGB)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(image_rgb)

            if encodings:  # Ensure a face is detected
                known_encodings.append(encodings[0])
                known_labels.append(str(person_id))

    return known_encodings, known_labels

# Load known faces
known_encodings, known_labels = load_known_faces()

# Initialize webcam with DirectShow backend for better performance (Windows fix)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FPS, 30)  # Ensure smoother frame rate

def process_faces(frame):
    """Threaded function to process face recognition asynchronously."""
    global face_locations, face_encodings, frame_skip_count, processed_frame
    rgb_small_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    with LOCK:
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        frame_skip_count = 0  # Reset frame skip count after processing
        processed_frame = frame.copy()  # Save processed frame for rendering

# Start face processing thread
processing_thread = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=FRAME_DOWNSCALE, fy=FRAME_DOWNSCALE, interpolation=cv2.INTER_LINEAR)

    # Run face recognition in a separate thread every `FRAME_SKIP` frames
    if frame_skip_count >= FRAME_SKIP:
        if processing_thread is None or not processing_thread.is_alive():
            processing_thread = threading.Thread(target=process_faces, args=(small_frame,))
            processing_thread.start()

    frame_skip_count += 1

    # Draw face rectangles from last processed frame
    with LOCK:
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.38)  # Stricter matching
            name = "Unknown"
            confidence = 0.0  # Default confidence for unknown faces

            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_labels[best_match_index]
                confidence = (1 - face_distances[best_match_index]) * 100  # Convert to percentage

            # Scale back the coordinates to match original frame size
            top, right, bottom, left = [int(coord / FRAME_DOWNSCALE) for coord in [top, right, bottom, left]]

            # Draw rectangle around the face
            color = TEXT_COLOR if name != "Unknown" else UNKNOWN_COLOR
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Display name and confidence level
            text = f"{name} ({confidence:.2f}%)"
            cv2.putText(frame, text, (left, top - 10), FONT, 0.6, color, 2)

    # Show the frame
    cv2.imshow("Face Recognition", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
