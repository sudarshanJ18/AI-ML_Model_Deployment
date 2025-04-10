import cv2
import os

dataset_path = "dataset"
os.makedirs(dataset_path, exist_ok=True)

# Ask for person name
person_name = input("Enter person name: ")

# Initialize webcam
cap = cv2.VideoCapture(0)
count = 0

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("Collecting face data. Press 'q' to quit.")

while count < 50:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame from camera. Check camera connection.")
        break
    
    # Display count on frame
    cv2.putText(frame, f"Captured: {count}/50", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    for (x, y, w, h) in faces:
        # Draw rectangle around detected face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Extract and save face
        face = frame[y:y+h, x:x+w]
        face = cv2.resize(face, (160, 160))
        cv2.imwrite(f"{dataset_path}/{person_name}_{count}.jpg", face)
        count += 1
        
        # Break if we've collected enough faces
        if count >= 50:
            break
    
    # Display frame
    cv2.imshow("Collecting Faces", frame)
    
    # Check for key press, wait for 100ms
    key = cv2.waitKey(100) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"Collected {count} face images for {person_name}")