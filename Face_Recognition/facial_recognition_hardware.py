import face_recognition
import cv2
import numpy as np
import time
import pickle
import pyrebase
from datetime import datetime

# Firebase configuration
config = {
    "apiKey": "AIzaSyA8y1iepfXtlSURONUiN3YRHjI7IunC1gE",
    "authDomain": "esp32-dht-47e5d.firebaseapp.com",
    "databaseURL": "https://esp32-dht-47e5d-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "esp32-dht-47e5d",
    "storageBucket": "esp32-dht-47e5d.firebasestorage.app",
    "messagingSenderId": "577240316281",
    "appId": "1:577240316281:web:2704461c2a866ed71f57a8",
    "measurementId":  "G-VKP0QN2QQ2"
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

# Initialize the authorized MSSV list (from Firebase)
authorized_mssv = {}

def update_authorized_mssv():
    global authorized_mssv
    try:
        # Fetch the list of employees from 'employees' node
        employees_data = database.child("employees").get().val()
        
        if employees_data:
            # Extract MSSV data (MSSV -> {mssv, name, registerDate, timeIn})
            # This assumes that 'employees' contains MSSV as the key for each employee
            authorized_mssv = {}
            for mssv, employee_data in employees_data.items():
                authorized_mssv[mssv] = employee_data
            print("[INFO] Authorized employees updated:", authorized_mssv)
        else:
            print("[INFO] No authorized employees found.")
    except Exception as e:
        print(f"[ERROR] Failed to update authorized employees: {e}")

# Variables for face recognition
face_locations = []
face_encodings = []
face_names = []
frame_count = 0
start_time = time.time()
fps = 0

def process_frame(frame):
    global face_locations, face_encodings, face_names, authorized_mssv
    
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
        mssv = "Unknown"
        
        if matches:
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                mssv = known_face_names[best_match_index]  # Using name as MSSV (or if you have another MSSV list, use that)
                
                # Check if the detected face's MSSV exists in authorized employees
                if mssv in authorized_mssv:
                    employee_info = authorized_mssv[mssv]
                    name = employee_info["name"]
                    register_date = employee_info["registerDate"]
                    time_in = employee_info["timeIn"]
                    
                    # Format current time as mm/dd/yyyy hh:mm
                    current_time = datetime.now().strftime('%m/%d/%Y %H:%M')
                    
                    # Update the timeIn for the employee
                    database.child("employees").child(mssv).update({"timeIn": current_time})
                    
                    # Print employee details
                    print(f"Authorized face detected: {name} (MSSV: {mssv}), Registered on: {register_date}, Time In: {time_in}")
                    print(f"Current time: {current_time}")
        
        face_names.append(mssv)
    
    return frame

# Call the update function periodically to ensure the list of authorized users is up-to-date
update_authorized_mssv()

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
