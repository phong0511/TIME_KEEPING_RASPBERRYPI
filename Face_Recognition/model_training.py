import os
from imutils import paths
import face_recognition
import pickle
import cv2

# Đường dẫn đến folder dataset
dataset_path = "dataset"

# Đường dẫn file để lưu danh sách các file đã xử lý
processed_images_file = "processed_images.txt"

# Đường dẫn file encodings
encodings_file = "encodings.pickle"

# Đọc danh sách các file đã xử lý trước đó
if os.path.exists(processed_images_file):
    with open(processed_images_file, "r") as file:
        processed_images = set(file.read().strip().split("\n"))
else:
    processed_images = set()

# Đọc encodings đã lưu trước đó (nếu có)
if os.path.exists(encodings_file):
    with open(encodings_file, "rb") as f:
        data = pickle.load(f)
        knownEncodings = data["encodings"]
        knownNames = data["names"]
else:
    knownEncodings = []
    knownNames = []

print("[INFO] Start processing new faces...")

# Lấy danh sách tất cả các file hình ảnh trong folder dataset
imagePaths = list(paths.list_images(dataset_path))

# Chỉ lấy những file chưa được xử lý
new_imagePaths = [imagePath for imagePath in imagePaths if imagePath not in processed_images]

if not new_imagePaths:
    print("[INFO] No new images to process. Training is up-to-date.")
else:
    for (i, imagePath) in enumerate(new_imagePaths):
        print(f"[INFO] Processing new image {i + 1}/{len(new_imagePaths)}")
        name = imagePath.split(os.path.sep)[-2]
        
        image = cv2.imread(imagePath)
        if image is None:
            print(f"[WARNING] Unable to read image {imagePath}. Skipping.")
            continue

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect face locations and compute encodings
        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)
        
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)

        # Thêm file đã xử lý vào danh sách
        processed_images.add(imagePath)

    # Cập nhật danh sách file đã xử lý
    with open(processed_images_file, "w") as file:
        file.write("\n".join(processed_images))

    # Lưu encodings mới vào file pickle
    print("[INFO] Serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    with open(encodings_file, "wb") as f:
        f.write(pickle.dumps(data))

    print(f"[INFO] Training complete. {len(new_imagePaths)} new images processed and saved to '{encodings_file}'")
