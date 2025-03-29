import cv2
import pickle
import face_recognition
import numpy as np

# Settings
TEXT_COLOR = (0, 255, 0)  # Green for recognized
UNKNOWN_COLOR = (0, 0, 255)  # Red for unknown
FONT = cv2.FONT_HERSHEY_SIMPLEX
FRAME_SCALE = 0.5  # Smaller = Faster
MIN_CONFIDENCE = 60  # Only accept matches with ≥70% confidence

# Load precomputed encodings
print("Loading known faces...")
with open('EncodeFile.p', 'rb') as f:
    known_data = pickle.load(f)

known_encodings = list(known_data.values())
known_labels = list(known_data.keys())
print(f"Loaded {len(known_labels)} known faces")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Downscale for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find faces in the frame
    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare with known faces
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_idx = np.argmin(face_distances)
        confidence = (1 - face_distances[best_match_idx]) * 100


        if confidence >= MIN_CONFIDENCE:
            name = known_labels[best_match_idx]
            color = TEXT_COLOR
            print("User",name,"has been detected with a confidence level of ",confidence)
        else:
            name = "Unknown"
            color = UNKNOWN_COLOR

        # Scale back to original frame size
        top, right, bottom, left = [int(x / FRAME_SCALE) for x in [top, right, bottom, left]]
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, f"{name} ({confidence:.1f}%)", (left, top - 10), FONT, 0.5, color, 1)

    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
<<<<<<< HEAD
cv2.destroyAllWindows()


def ID_from_Image():
    return name
=======
cv2.destroyAllWindows()
>>>>>>> e05bbb43e9f8fe8c4b79eda6b69e3d5e49433a7b
