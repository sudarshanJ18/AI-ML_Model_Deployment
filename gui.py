import tkinter as tk
from tkinter import filedialog, Label, Button, Frame
import cv2
import numpy as np
from PIL import Image, ImageTk
import pickle
import os
from utils import get_embedding, detect_faces, extract_face

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        root.title("Face Recognition Demo")
        root.geometry("600x550")
        root.configure(padx=20, pady=20)
        
        # Try to load models
        self.load_models()
        
        # Main frame
        main_frame = Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = Label(main_frame, text="Face Recognition Demo", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Status label to show model loading status
        self.status_label = Label(main_frame, text="", font=("Arial", 10), fg="gray")
        self.status_label.pack(pady=5)
        self.update_status()
        
        # Buttons frame
        button_frame = Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Upload button
        self.upload_btn = Button(button_frame, text="Upload & Recognize", command=self.upload_and_recognize, 
                                 bg="#4CAF50", fg="white", font=("Arial", 12), padx=10, pady=5)
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        # Webcam button
        self.webcam_btn = Button(button_frame, text="Webcam Recognition", command=self.start_webcam, 
                                 bg="#2196F3", fg="white", font=("Arial", 12), padx=10, pady=5)
        self.webcam_btn.pack(side=tk.LEFT, padx=5)
        
        # Image display label
        self.img_label = Label(main_frame, bg="#f0f0f0", width=500, height=300)
        self.img_label.pack(pady=10)
        
        # Result label
        self.result_label = Label(main_frame, text="Upload an image or start webcam", font=("Arial", 14))
        self.result_label.pack(pady=10)
        
        # Webcam variables
        self.is_webcam_running = False
        self.cap = None
        
    def load_models(self):
        """Load the required models for face recognition"""
        try:
            # Check if model files exist
            if not os.path.exists("models/svm_model.pkl") or not os.path.exists("models/label_encoder.pkl"):
                self.svm_model = None
                self.label_encoder = None
                print("Models not found. Please train the model first.")
                return
            
            # Load SVM model
            with open("models/svm_model.pkl", "rb") as f:
                self.svm_model = pickle.load(f)
            
            # Load label encoder
            with open("models/label_encoder.pkl", "rb") as f:
                self.label_encoder = pickle.load(f)
                
            print("Models loaded successfully")
        except Exception as e:
            self.svm_model = None
            self.label_encoder = None
            print(f"Error loading models: {e}")
    
    def update_status(self):
        """Update the status label based on model loading status"""
        if self.svm_model is None or self.label_encoder is None:
            self.status_label.config(text="Models not loaded. Please train the model first.", fg="red")
        else:
            self.status_label.config(text=f"Models loaded. {len(self.label_encoder.classes_)} people in database.", fg="green")
    
    def recognize_face_in_image(self, image):
        """Recognize faces in an image"""
        if self.svm_model is None or self.label_encoder is None:
            return "Models not loaded. Please train the model first."
        
        # Detect faces
        faces = detect_faces(image)
        
        if len(faces) == 0:
            return "No face detected in the image"
        
        results = []
        
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Extract face
            face_img = extract_face(image, (x, y, w, h))
            
            # Get face embedding
            embedding = get_embedding(face_img)
            
            # Predict with SVM
            prediction = self.svm_model.predict_proba([embedding])[0]
            best_class_idx = np.argmax(prediction)
            best_class_prob = prediction[best_class_idx]
            
            if best_class_prob < 0.5:
                name = "Unknown"
            else:
                name = self.label_encoder.inverse_transform([best_class_idx])[0]
                
            result = f"{name} ({best_class_prob:.2f})"
            results.append(result)
            
            # Draw name on image
            cv2.putText(image, result, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        return ", ".join(results)
    
    def upload_and_recognize(self):
        """Upload an image and recognize faces"""
        # Stop webcam if it's running
        self.stop_webcam()
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")]
        )
        
        if not file_path:
            return
        
        try:
            # Read image
            image = cv2.imread(file_path)
            if image is None:
                self.result_label.config(text="Error: Could not read image")
                return
            
            # Recognize faces
            result = self.recognize_face_in_image(image)
            
            # Convert to RGB for display
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize image for display
            image = self.resize_image_for_display(image)
            
            # Convert to PhotoImage
            pil_image = Image.fromarray(image)
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # Update UI
            self.img_label.config(image=tk_image)
            self.img_label.image = tk_image
            self.result_label.config(text=f"Recognized: {result}")
            
        except Exception as e:
            self.result_label.config(text=f"Error: {str(e)}")
    
    def resize_image_for_display(self, image, max_width=500, max_height=300):
        """Resize image while maintaining aspect ratio"""
        height, width = image.shape[:2]
        
        # Calculate aspect ratio
        aspect_ratio = width / height
        
        # Determine new dimensions
        if width > height:
            new_width = min(width, max_width)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = min(height, max_height)
            new_width = int(new_height * aspect_ratio)
        
        # Resize image
        return cv2.resize(image, (new_width, new_height))
    
    def start_webcam(self):
        """Start webcam-based face recognition"""
        if self.is_webcam_running:
            return
        
        try:
            # Initialize webcam
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.result_label.config(text="Error: Could not open webcam")
                return
            
            self.is_webcam_running = True
            self.webcam_btn.config(text="Stop Webcam", bg="#F44336")
            self.result_label.config(text="Webcam running. Press 'Stop Webcam' to stop.")
            
            # Start webcam loop
            self.update_webcam_frame()
            
        except Exception as e:
            self.result_label.config(text=f"Error: {str(e)}")
            self.stop_webcam()
    
    def update_webcam_frame(self):
        """Update webcam frame in UI"""
        if not self.is_webcam_running:
            return
        
        try:
            # Read frame from webcam
            ret, frame = self.cap.read()
            if not ret:
                self.stop_webcam()
                return
            
            # Make a copy for processing
            processed_frame = frame.copy()
            
            # Detect and recognize faces
            faces = detect_faces(processed_frame)
            
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Extract face
                face_img = extract_face(processed_frame, (x, y, w, h))
                
                # Recognize face if models are loaded
                if self.svm_model is not None and self.label_encoder is not None:
                    # Get face embedding
                    embedding = get_embedding(face_img)
                    
                    # Predict with SVM
                    prediction = self.svm_model.predict_proba([embedding])[0]
                    best_class_idx = np.argmax(prediction)
                    best_class_prob = prediction[best_class_idx]
                    
                    if best_class_prob < 0.5:
                        name = "Unknown"
                    else:
                        name = self.label_encoder.inverse_transform([best_class_idx])[0]
                        
                    result = f"{name} ({best_class_prob:.2f})"
                    
                    # Draw name on image
                    cv2.putText(processed_frame, result, (x, y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Convert to RGB for display
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            
            # Resize for display
            processed_frame = self.resize_image_for_display(processed_frame)
            
            # Convert to PhotoImage
            pil_image = Image.fromarray(processed_frame)
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # Update UI
            self.img_label.config(image=tk_image)
            self.img_label.image = tk_image
            
            # Schedule next update
            self.root.after(33, self.update_webcam_frame)  # ~30 FPS
            
        except Exception as e:
            print(f"Error in webcam loop: {e}")
            self.stop_webcam()
    
    def stop_webcam(self):
        """Stop webcam capture"""
        if self.is_webcam_running:
            self.is_webcam_running = False
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.webcam_btn.config(text="Webcam Recognition", bg="#2196F3")
            self.result_label.config(text="Webcam stopped")

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()