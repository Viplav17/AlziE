import cv2
import face_recognition
import pickle
import os

folderPath = 'Picture_Source'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []

print("Encoding Started...")

for path in pathList:
    img = cv2.imread(f'{folderPath}/{path}')
    imgList.append(img)
    studentIds.append(os.path.splitext(path)[0])

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]

with open('EncodeFile.p', 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)

print("Encoding Completed!")









