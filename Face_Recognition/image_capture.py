import cv2
import os
from datetime import datetime

# Change this to the name of the person you're photographing test...
PERSON_NAME = "qui"

def create_folder(name):
    dataset_folder = "dataset"
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)
    
    person_folder = os.path.join(dataset_folder, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

def capture_photos(name):
    folder = create_folder(name)
    
    # Initialize the laptop's camera
    camera = cv2.VideoCapture(0)  # '0' is the default camera. Change to '1', '2', etc., for other cameras.
    
    if not camera.isOpened():
        print("Error: Unable to access the camera.")
        return
    
    print(f"Taking photos for {name}. Press SPACE to capture, 'q' to quit.")
    
    photo_count = 0
    
    while True:
        # Capture frame from camera
        ret, frame = camera.read()
        if not ret:
            print("Error: Unable to capture frame.")
            break
        
        # Display the frame
        cv2.imshow('Capture', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # Space keyyyyy
            photo_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.jpg"
            filepath = os.path.join(folder, filename)
            cv2.imwrite(filepath, frame)
            print(f"Photo {photo_count} saved: {filepath}")
        
        elif key == ord('q'):  # Q key
            break
    
    # Clean up
    camera.release()
    cv2.destroyAllWindows()
    print(f"Photo capture completed. {photo_count} photos saved for {name}.")

if __name__ == "__main__":
    capture_photos(PERSON_NAME)
