import cv2
import face_recognition
import numpy as np
import os
import logging
import mediapipe as mp

# Constants
TEXT_COLOR = (0, 255, 0)  # Green for recognized faces
UNKNOWN_COLOR = (0, 0, 255)  # Red for unknown faces
FONT = cv2.FONT_HERSHEY_SIMPLEX
FRAME_DOWNSCALE = 1  # Downscale the frame to improve performance
FRAME_SKIP = 2  # Process every 3rd frame to reduce workload
FACE_TOLERANCE = 0.38  # Stricter matching tolerance for face recognition

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load known face images and encode them
def load_known_faces(image_folder="Picture_Source"):
    known_encodings = []
    known_labels = []

    # Check if the directory exists
    if not os.path.isdir(image_folder):
        logging.error(f"Directory '{image_folder}' not found.")
        return known_encodings, known_labels

    # Get all image files from subdirectories
    image_paths = []
    for dirpath, _, filenames in os.walk(image_folder):
        for file in filenames:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):  # Add other image formats if needed
                image_paths.append(os.path.join(dirpath, file))

    # Process all images
    for image_path in image_paths:
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:  # If faces are found
                person_id = os.path.basename(os.path.dirname(image_path))  # Assuming folder name as label
                known_encodings.append(encodings[0])
                known_labels.append(person_id)
                logging.info(f"Loaded face encoding for {person_id} from {image_path}")
        except Exception as e:
            logging.error(f"Error processing {image_path}: {e}")

    return known_encodings, known_labels

# Load known faces
known_encodings, known_labels = load_known_faces()

if not known_encodings:
    logging.error("No known faces found. Exiting.")
    exit()

# Initialize webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FPS, 30)  # Ensure smoother frame rate

# Check if the webcam is opened correctly
if not cap.isOpened():
    logging.error("Error: Could not open webcam.")
    exit()

# Initialize MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

frame_skip_count = 0  # Counter to skip frames
last_known_face_position = None  # To store the last known face position

while True:
    ret, frame = cap.read()
    if not ret:
        logging.error("Error: Failed to capture image.")
        break

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=FRAME_DOWNSCALE, fy=FRAME_DOWNSCALE, interpolation=cv2.INTER_LINEAR)

    # Only process every `FRAME_SKIP`-th frame
    if frame_skip_count % FRAME_SKIP == 0:
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Use MediaPipe FaceMesh to detect faces and facial landmarks
        results = face_mesh.process(rgb_small_frame)

        if results.multi_face_landmarks:
            # For each detected face, check the face recognition
            for face_landmarks in results.multi_face_landmarks:
                # Draw face mesh landmarks (optional, for debugging)
                mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS)

                # Use the landmarks to create a bounding box
                # We focus on the region of interest using specific landmarks (eyes, nose, etc.)
                face_location = (
                    int(face_landmarks.landmark[1].x * frame.shape[1]),
                    int(face_landmarks.landmark[1].y * frame.shape[0]),
                    int(face_landmarks.landmark[5].x * frame.shape[1]),
                    int(face_landmarks.landmark[5].y * frame.shape[0])
                )

                # Encode the face for recognition
                face_encoding = face_recognition.face_encodings(frame, [face_location])

                if face_encoding:
                    matches = face_recognition.compare_faces(known_encodings, face_encoding[0], tolerance=FACE_TOLERANCE)
                    name = "Unknown"
                    confidence = 0.0  # Default confidence for unknown faces

                    # Calculate face distance and choose best match
                    face_distances = face_recognition.face_distance(known_encodings, face_encoding[0])
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = known_labels[best_match_index]
                        confidence = (1 - face_distances[best_match_index]) * 100  # Convert to percentage

                    # Scale back the coordinates to match the original frame size
                    top, right, bottom, left = face_location
                    # Update last known face position
                    last_known_face_position = (top, right, bottom, left)

                    # Draw rectangle around the face
                    color = TEXT_COLOR if name != "Unknown" else UNKNOWN_COLOR
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                    # Display name and confidence level
                    text = f"{name} ({confidence:.2f}%)"
                    cv2.putText(frame, text, (left, top - 10), FONT, 0.6, color, 2)

        else:
            logging.info("No faces detected in this frame.")

    elif last_known_face_position:
        # If no face is detected, use the last known face position and keep the bounding box
        top, right, bottom, left = last_known_face_position

        # Draw rectangle around the last known face
        color = TEXT_COLOR if name != "Unknown" else UNKNOWN_COLOR
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Display name and confidence level (we can show the last known values or Unknown if we can't confirm)
        text = f"{name} ({confidence:.2f}%)" if last_known_face_position else "Unknown"
        cv2.putText(frame, text, (left, top - 10), FONT, 0.6, color, 2)

    # Increment frame skip counter
    frame_skip_count += 1

    # Show the frame
    cv2.imshow("Face Recognition with MediaPipe", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
