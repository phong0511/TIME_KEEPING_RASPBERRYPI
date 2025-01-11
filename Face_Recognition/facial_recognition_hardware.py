import face_recognition
import cv2
import numpy as np
import time
import pickle
import pyrebase
from datetime import datetime

# Firebase configuration
config = {
    "apiKey": "AIzaSyDhiVY-HO6C8aSiP8sOMo5Buxucimqn_F8",
    "authDomain": "timekeeping-project-81830.firebaseapp.com",
    "databaseURL": "https://timekeeping-project-81830-default-rtdb.firebaseio.com",
    "projectId": "timekeeping-project-81830",
    "storageBucket": "timekeeping-project-81830.firebasestorage.app",
    "messagingSenderId": "957110757990",
    "appId": "1:957110757990:web:21a831c14fa5110b9d5ba7",
    "measurementId":  "G-2Y17NX87X7"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
database = firebase.database()

# Load pre-trained face encodings
print("[INFO] Loading encodings...")
with open("encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())   
known_face_encodings = data["encodings"]
known_face_names = data["names"]

# Initialize the camera
print("[INFO] Starting camera...")
video_capture = cv2.VideoCapture(0)  # Use webcam (camera index 0)

# Parameters
cv_scaler = 4  # Resize factor for performance
authorized_names = ["thang", "phong", "qui"]  # Replace with names you want to authorize

# Variables for face recognition
face_locations = []
face_encodings = []
face_names = []
frame_count = 0
start_time = time.time()
fps = 0

def process_frame(frame):
    global face_locations, face_encodings, face_names
    
    # Resize the frame for faster processing
    resized_frame = cv2.resize(frame, (0, 0), fx=1/cv_scaler, fy=1/cv_scaler)
    rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    
    # Detect faces and compute encodings
    face_locations = face_recognition.face_locations(rgb_resized_frame)
    face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations, model='large')
    
    face_names = []
    authorized_face_detected = False
    
    for face_encoding in face_encodings:
        key = cv2.waitKey(1) & 0xFF
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        
        if matches:
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                
                # Check if the detected face is authorized
                if name in authorized_names:
                   if key == ord('x'):
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        data_name = name
                        data_time = {"current_time": current_time}
                        database.child("time_logs").set(data_time)
                        authorized_face_detected = True
                        database.child("Test_face")
                        database.set(data_name)
                        print(name)
        
        face_names.append(name)
    
    # Control GPIO based on face detection

    return frame

def draw_results(frame):
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up the face locations
        top *= cv_scaler
        right *= cv_scaler
        bottom *= cv_scaler
        left *= cv_scaler
        
        # Draw rectangle and label
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
    return frame

def calculate_fps():
    global frame_count, start_time, fps
    frame_count += 1
    elapsed_time = time.time() - start_time
    if elapsed_time > 1:
        fps = frame_count / elapsed_time
        frame_count = 0
        start_time = time.time()
    return fps

while True:
    # Capture a single frame from the camera
    ret, frame = video_capture.read()
    if not ret:
        print("[ERROR] Unable to read from the camera.")
        break
    
    # Process the frame
    processed_frame = process_frame(frame)
    
    # Draw results on the frame
    display_frame = draw_results(processed_frame)
    
    # Calculate FPS
    current_fps = calculate_fps()
    cv2.putText(display_frame, f"FPS: {current_fps:.1f}", (display_frame.shape[1] - 150, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Display the video feed
    cv2.imshow('Video', display_frame)
    
    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) == ord("q"):
        break

# Cleanup
video_capture.release()
cv2.destroyAllWindows()
output.off()
