import cv2
import os
import sys

def detect_faces_in_image(image_path):
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return None
        
    # Load the face detector
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    except Exception as e:
        print(f"Error loading face detector: {e}")
        return None
    
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image: {image_path}")
        return None
        
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    
    # Draw rectangles around faces
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
    
    print(f"Detected {len(faces)} faces")
    
    # Show the image
    cv2.imshow('Detected Faces', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return image

if __name__ == "__main__":
    # If an image path is provided as argument, use it
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = 'test.jpg'
        
    detect_faces_in_image(image_path)