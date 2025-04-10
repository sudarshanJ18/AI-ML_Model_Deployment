from flask import Flask, request, jsonify
import cv2
import numpy as np
import pickle
from utils import get_embedding, detect_faces, extract_face
import os

app = Flask(__name__)

# Check if models exist
MODELS_DIR = "models"
SVM_MODEL_PATH = os.path.join(MODELS_DIR, "svm_model.pkl")
LABEL_ENCODER_PATH = os.path.join(MODELS_DIR, "label_encoder.pkl")

# Load models
try:
    if os.path.exists(SVM_MODEL_PATH):
        with open(SVM_MODEL_PATH, "rb") as f:
            svm_model = pickle.load(f)
    else:
        print(f"Warning: SVM model not found at {SVM_MODEL_PATH}")
        svm_model = None
        
    if os.path.exists(LABEL_ENCODER_PATH):
        with open(LABEL_ENCODER_PATH, "rb") as f:
            label_encoder = pickle.load(f)
    else:
        print(f"Warning: Label encoder not found at {LABEL_ENCODER_PATH}")
        label_encoder = None
except Exception as e:
    print(f"Error loading models: {e}")
    svm_model = None
    label_encoder = None

def recognize_face(image, threshold=0.5):
    """Recognize faces in an image using loaded models"""
    if svm_model is None or label_encoder is None:
        return "Unknown (Models not loaded)"
    
    # Detect faces using OpenCV
    faces = detect_faces(image)
    
    if len(faces) == 0:
        return "No face detected"
    
    # Get the largest face (assuming it's the most prominent)
    largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
    
    # Extract and process the face
    face_img = extract_face(image, largest_face)
    
    # Get embedding
    embedding = get_embedding(face_img)
    
    # Predict with SVM
    prediction = svm_model.predict_proba([embedding])[0]
    best_class_idx = np.argmax(prediction)
    best_class_prob = prediction[best_class_idx]
    
    if best_class_prob < threshold:
        return "Unknown"
    
    # Get the name from label encoder
    name = label_encoder.inverse_transform([best_class_idx])[0]
    return f"{name} ({best_class_prob:.2f})"

@app.route('/')
def home():
    return "Face Recognition API is Running!"

@app.route('/recognize', methods=['POST'])
def recognize_endpoint():
    """Recognize faces from an uploaded image."""
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    image_bytes = file.read()
    
    # Convert image to numpy array
    image = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
    if image is None:
        return jsonify({"error": "Invalid image format"}), 400

    # Detect all faces in the image
    faces = detect_faces(image)
    recognized_faces = []

    for (x, y, w, h) in faces:
        face_img = extract_face(image, (x, y, w, h))
        
        # Get face embedding
        embedding = get_embedding(face_img)
        
        # Predict with SVM if models are loaded
        if svm_model is not None and label_encoder is not None:
            prediction = svm_model.predict_proba([embedding])[0]
            best_class_idx = np.argmax(prediction)
            best_class_prob = prediction[best_class_idx]
            
            if best_class_prob < 0.5:
                name = "Unknown"
            else:
                name = label_encoder.inverse_transform([best_class_idx])[0]
                name = f"{name} ({best_class_prob:.2f})"
        else:
            name = "Unknown (Models not loaded)"

        recognized_faces.append({
            "name": name,
            "confidence": float(best_class_prob) if svm_model is not None else 0.0,
            "bounding_box": [int(x), int(y), int(w), int(h)]
        })

    return jsonify({
        "faces_detected": len(faces),
        "recognized_faces": recognized_faces
    })

@app.route('/webcam', methods=['GET'])
def webcam_recognition():
    """This endpoint returns instructions for webcam recognition"""
    return jsonify({
        "message": "Webcam recognition can't be run via API endpoint. Please run the webcam demo from the command line.",
        "instruction": "To run webcam recognition, use the webcam_demo.py script"
    })

def run_webcam_demo():
    """Run webcam-based face recognition demo"""
    if svm_model is None or label_encoder is None:
        print("Error: Models not loaded. Please train the model first.")
        return
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    print("Starting webcam face recognition. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect faces
        faces = detect_faces(frame)

        for (x, y, w, h) in faces:
            # Extract face
            face_img = extract_face(frame, (x, y, w, h))
            
            # Get face embedding
            embedding = get_embedding(face_img)
            
            # Predict with SVM
            prediction = svm_model.predict_proba([embedding])[0]
            best_class_idx = np.argmax(prediction)
            best_class_prob = prediction[best_class_idx]
            
            if best_class_prob < 0.5:
                name = "Unknown"
            else:
                name = label_encoder.inverse_transform([best_class_idx])[0]
                name = f"{name} ({best_class_prob:.2f})"
            
            # Draw rectangle and name
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Show frame
        cv2.imshow("Face Recognition", frame)
        
        # Check for key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--webcam':
        run_webcam_demo()
    else:
        print("Starting Face Recognition API server...")
        app.run(host='0.0.0.0', port=10000, debug=False)