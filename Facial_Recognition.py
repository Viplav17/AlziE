import cv2
import pickle
import face_recognition

cap = cv2.VideoCapture(0) 
cap.set(3,640)
cap.set(4,480)

# Load the encoding file
print("Loading the encoded file..... ")
file = open('EncodeFile.p','rb')
encodeListKnownwithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownwithIds
print(studentIds)

print("Encoded file complete")

# Loop to capture frames from the webcam
while True: 
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Resize image to reduce computation
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)  # Convert the image to RGB format for face_recognition

    faceCurrentFrame = face_recognition.face_locations(imgS)   # Detect faces in the current frame
    encodecurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)  # Get encodings of the current frame

    for encodeface, faceLoC in zip(encodecurrentFrame, faceCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeface)
        facedistance = face_recognition.face_distance(encodeListKnown, encodeface)

        print("matches", matches)
        print("facedistance", facedistance)

        # Check if there is a match
        if True in matches:
            first_match_index = matches.index(True)  # Get the index of the matched face
            name = studentIds[first_match_index]  # Get the name from studentIds list using the matched index
            print(f"Found {name} in the frame!")

            # You can now display the image associated with the matched face (if you have image files)
            # Assuming 'studentIds' is a list of names, and you have an image associated with each person

            # Load the image (assuming you have images named by the studentId or you can map the ids to file names)
            image_path = f"images/{name}.jpg"  # Update this line according to where your images are stored
            match_image = cv2.imread(image_path)  # Read the image
            if match_image is not None:
                cv2.imshow(f"Matched face: {name}", match_image)  # Show the matched image in a new window

        # Draw a rectangle around the face
        top, right, bottom, left = faceLoC
        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)  # Draw rectangle

    # Show the live video stream with the rectangle drawn around faces
    cv2.imshow("Facial Recognition", img)
    cv2.waitKey(1)
