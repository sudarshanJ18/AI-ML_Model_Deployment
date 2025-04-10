import cv2
import numpy as np
import pickle
import os
from utils import get_embedding, detect_faces, extract_face

def main():
    """Run a standalone webcam face recognition demo"""
    # Check if models exist
    if not os.path.exists("models/svm_model.pkl") or not os.path.exists("models/label_encoder.pkl"):
        print("Error: Models not found in the 'models' directory.")
        print("Please run train_model.py first to create the models.")
        return
    
    # Load models
    try:
        with open("models/svm_model.pkl", "rb") as f:
            svm_model = pickle.load(f)
        with open("models/label_encoder.pkl", "rb") as f:
            label_encoder = pickle.load(f)
        print("Models loaded successfully")
    except Exception as e:
        print(f"Error loading models: {e}")
        return
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Starting webcam face recognition. Press 'q' to quit.")
    
    while True:
        # Read frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read from webcam")
            break
        
        # Detect faces
        faces = detect_faces(frame)
        
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Extract face
            face_img = extract_face(frame, (x, y, w, h))
            
            # Get face embedding
            embedding = get_embedding(face_img)
            
            # Predict with SVM
            prediction = svm_model.predict_proba([embedding])[0]
            best_class_idx = np.argmax(prediction)
            best_class_prob = prediction[best_class_idx]
            
            # Set confidence threshold
            if best_class_prob < 0.5:
                name = "Unknown"
            else:
                name = label_encoder.inverse_transform([best_class_idx])[0]
                name = f"{name} ({best_class_prob:.2f})"
            
            # Display name above face
            cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Show frame
        cv2.imshow("Face Recognition", frame)
        
        # Check for key press (q to quit)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam demo closed")

if __name__ == "__main__":
    main()