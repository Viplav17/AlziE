import cv2 
import face_recognition
import pickle 
import os

#importing images 

folderPath = 'Picture_Source'
PathList = os.listdir(folderPath)
print(PathList)
imgList = []
studentIds = []    
for path in PathList: 
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    #print(path)
    #print(os.path.splitext(path)[0])
    studentIds.append(os.path.splitext(path)[0])  #getting ids and putting that in studentIds.append

print(studentIds)


def findEncodings(imagesList): 

    for image in imagesList: 
        encodeList = []
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encodeList.append(encode)


    return encodeList

print("Encoding has started ....")

encodeListKnown = findEncodings(imgList) 
encodeListKnownwithIds = [encodeListKnown, studentIds]

file = open('EncodeFile.p','wb')
pickle.dump(encodeListKnownwithIds,file)
file.close()

print("File Saved")


print(encodeListKnown)

print("Encodings complete")
        








