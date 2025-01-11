import face_recognition
import cv2
import numpy as np
import time
import pickle

# Load pre-trained face encodings
print("[INFO] loading encodings...")
with open("encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())
known_face_encodings = data["encodings"]
known_face_names = data["names"]

# Initialize the camera (use 0 for default laptop camera)
video_capture = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not video_capture.isOpened():
    print("[ERROR] Unable to access the camera.")
    exit()

# Initialize our variables
cv_scaler = 4  # Scale down factor for performance optimization
face_locations = []
face_encodings = []
face_names = []
frame_count = 0
start_time = time.time()
fps = 0
def process_frame(frame):
    global face_locations, face_encodings, face_names
    

    try:
        print(f"Frame dtype: {frame.dtype}, Frame shape: {frame.shape}")
        # Resize the frame to increase performance
        resized_frame = cv2.resize(frame, (0, 0), fx=(1/cv_scaler), fy=(1/cv_scaler))
        
        # Convert the frame to RGB
        rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_resized_frame)
        face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations)
        
        face_names = []
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            
            # Find the best match
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            face_names.append(name)
    
    except Exception as e:
        print(f"[ERROR] Error processing frame: {e}")
        face_locations = []
        face_names = []
    
    return frame

def draw_results(frame):
    # Display results on the frame
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations to match the original frame
        print(f"Frame dtype: {frame.dtype}, Frame shape: {frame.shape}")
        top *= cv_scaler
        right *= cv_scaler
        bottom *= cv_scaler
        left *= cv_scaler
        
        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 3)
        
        # Draw a label with a name below the face
        cv2.rectangle(frame, (left - 3, top - 35), (right + 3, top), (244, 42, 3), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)
    
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

# Clean up
video_capture.release()
cv2.destroyAllWindows()
