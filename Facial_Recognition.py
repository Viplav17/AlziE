import cv2
import pickle
import face_recognition
import numpy as np
import cvzone

cap = cv2.VideoCapture(0)
cap.set(3, 480)  # Lowered resolution for smoother performance
cap.set(4, 360)

# Load the encoding file
print("Loading the encoded file...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownwithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownwithIds
print("Known IDs:", studentIds)
print("Encoded file loaded successfully.")

frame_count = 0

# Use a smaller resolution for the frame (to boost performance)
frame_width = 320
frame_height = 240

# Capture frame at lower resolution
cap.set(3, frame_width)  # Width
cap.set(4, frame_height)  # Height

# Use NumPy arrays for better performance
encodeListKnown = np.array(encodeListKnown)

while True:
    success, img = cap.read()
    if not success:
        break

    frame_count += 1

    # Process every 3rd frame for better performance
    if frame_count % 3 == 0:
        # Resize the image for faster processing
        imgS = cv2.resize(img, (frame_width, frame_height))
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # Detect faces and encodings
        faceCurrentFrame = face_recognition.face_locations(imgS)
        encodecurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)

        for encodeface, faceLoc in zip(encodecurrentFrame, faceCurrentFrame):
            # Compare the detected face with known faces using NumPy for efficient comparison
            faceDistance = face_recognition.face_distance(encodeListKnown, encodeface)
            min_distance = np.min(faceDistance)

            name = "Unknown"
            threshold = 0.45  # You can adjust this threshold based on your requirements

            # If the closest match is below the threshold, identify it
            if min_distance < threshold:
                matchIndex = np.argmin(faceDistance)
                name = str(studentIds[matchIndex])
                confidence = round((1 - min_distance) * 100, 2)
                print(f'Found {name} with confidence: {confidence}%')

            # Scale back to original size for bounding box
            top, right, bottom, left = faceLoc
            top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4

            # Draw rectangle and ID on the original image
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show webcam
    cv2.imshow("Facial Recognition", img)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
