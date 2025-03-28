import cv2
import pickle
import face_recognition

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load Encodings
with open('EncodeFile.p', 'rb') as file:
    encodeListKnown, studentIds = pickle.load(file)

print("Encodings Loaded...")

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgS)
    encodeCurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)

    for encodeFace, faceLoc in zip(encodeCurrentFrame, faceCurrentFrame):
        faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
        minDistance = min(faceDistance)
        matchIndex = faceDistance.tolist().index(minDistance)

        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

        if minDistance < 0.45:
            name = studentIds[matchIndex]
            color = (0, 255, 0)
        else:
            name = "Unknown"
            color = (0, 0, 255)

        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Facial Recognition", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
