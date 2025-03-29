import cv2
import face_recognition
import pickle
import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor

def main():
    # Configuration
    folderPath = 'Picture_Source'
    output_file = 'EncodeFile.p'
    
    # Verify folder exists
    if not os.path.exists(folderPath):
        print(f"Error: Folder '{folderPath}' not found!")
        print("Please create the folder and add person subfolders with images.")
        return
    
    pathList = os.listdir(folderPath)
    if not pathList:
        print(f"No person folders found in '{folderPath}'")
        return
    
    print(f"Found {len(pathList)} persons in '{folderPath}'")

    def process_image(img_path, person_id):
        """Process a single image and return its face encoding"""
        try:
            img = cv2.imread(img_path)
            if img is None:
                return None, None
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(img_rgb, model='hog')
            
            if not face_locations:
                return None, None
            
            face_encodings = face_recognition.face_encodings(img_rgb, face_locations)
            if not face_encodings:
                return None, None
            
            return face_encodings[0], person_id  # Take first face found
        except Exception as e:
            print(f"Error processing {img_path}: {str(e)}")
            return None, None

    def process_person(person_id):
        """Process all images for one person"""
        person_path = os.path.join(folderPath, person_id)
        if not os.path.isdir(person_path):
            return []
        
        encodings = []
        valid_images = 0
        
        for img_file in os.listdir(person_path):
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(person_path, img_file)
                encoding, _ = process_image(img_path, person_id)
                if encoding is not None:
                    encodings.append(encoding)
                    valid_images += 1
        
        print(f"Processed {valid_images} valid images for {person_id}")
        return encodings

    print("Encoding Started (Using Parallel Processing)...")

    # Process persons in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        all_encodings = list(executor.map(process_person, pathList))

    # Group encodings by person ID
    encodings_dict = {}
    for person_id, encodings in zip(pathList, all_encodings):
        if encodings:
            encodings_dict[person_id] = np.mean(encodings, axis=0)  # Average encodings

    # Save the results
    with open(output_file, 'wb') as file:
        pickle.dump(encodings_dict, file)

    print(f"\nEncoding Completed! Processed {len(encodings_dict)} persons:")
    for person_id in encodings_dict:
        print(f"- {person_id}")

if __name__ == "__main__":
    main()