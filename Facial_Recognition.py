import cv2
import pickle
import face_recognition

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load the encoding file
print("Loading the encoded file...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownwithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownwithIds
print("Known IDs:", studentIds)
print("Encoded file loaded successfully.")

# Webcam loop
while True:
    success, img = cap.read()

    # Resize and convert for face_recognition processing
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect faces and encode
    faceCurrentFrame = face_recognition.face_locations(imgS)
    encodecurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)

    # Loop through detected faces
    for encodeface, faceLoc in zip(encodecurrentFrame, faceCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeface)
        faceDistance = face_recognition.face_distance(encodeListKnown, encodeface)

        name = "Unknown"

        # If match found
        if True in matches:
            matchIndex = matches.index(True)
            name = str(studentIds[matchIndex])
            print('Found a match')
            print(name)

        # Scale back face location to original image size
        top, right, bottom, left = faceLoc
        top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4

        # Draw rectangle and ID
        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show webcam
    cv2.imshow("Facial Recognition", img)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
