import tkinter as tk
from tkinter import filedialog, Label, Button, Frame, ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import pickle
import os
from utils import get_embedding, detect_faces, extract_face

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        root.title("Face Recognition System")
        root.geometry("800x700")
        root.configure(bg="#f5f5f5")
        
        # Set application icon if available
        try:
            root.iconbitmap("app_icon.ico")
        except:
            pass
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TButton", font=("Segoe UI", 11))
        self.style.configure("TLabel", background="#f5f5f5", font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"))
        self.style.configure("Status.TLabel", font=("Segoe UI", 10))
        
        # Try to load models
        self.load_models()
        
        # Main container
        main_container = ttk.Frame(root, padding=20, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with logo and title
        header_frame = ttk.Frame(main_container, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # App title
        title_label = ttk.Label(header_frame, text="Face Recognition System", style="Header.TLabel")
        title_label.pack(side=tk.LEFT, pady=10)
        
        # Status indicator
        status_frame = ttk.Frame(main_container, style="TFrame")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_label = ttk.Label(status_frame, text="System Status:", style="TLabel")
        status_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="", style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)
        self.update_status()
        
        # Control panel
        control_frame = ttk.Frame(main_container, style="TFrame")
        control_frame.pack(fill=tk.X, pady=10)
        
        # Main buttons
        self.upload_btn = ttk.Button(
            control_frame, 
            text="Upload Image", 
            command=self.upload_and_recognize,
            style="TButton"
        )
        self.upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.webcam_btn = ttk.Button(
            control_frame, 
            text="Start Webcam", 
            command=self.start_webcam,
            style="TButton"
        )
        self.webcam_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Additional buttons
        self.collect_btn = ttk.Button(
            control_frame, 
            text="Collect Faces", 
            command=self.collect_faces,
            style="TButton"
        )
        self.collect_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.train_btn = ttk.Button(
            control_frame, 
            text="Train Model", 
            command=self.train_model,
            style="TButton"
        )
        self.train_btn.pack(side=tk.LEFT)
        
        # Display frame
        display_frame = ttk.Frame(main_container, style="TFrame")
        display_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Image display with border
        img_frame = ttk.Frame(display_frame, borderwidth=2, relief="groove")
        img_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.img_label = Label(img_frame, bg="#e0e0e0")
        self.img_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Results section
        results_frame = ttk.Frame(main_container, style="TFrame")
        results_frame.pack(fill=tk.X, pady=10)
        
        results_header = ttk.Label(results_frame, text="Recognition Results:", style="TLabel")
        results_header.pack(anchor=tk.W, pady=(0, 5))
        
        self.result_label = ttk.Label(
            results_frame, 
            text="Upload an image or start webcam to begin recognition",
            style="TLabel"
        )
        self.result_label.pack(anchor=tk.W)
        
        # Footer
        footer_frame = ttk.Frame(main_container, style="TFrame")
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        footer_text = ttk.Label(
            footer_frame, 
            text="© 2023 Face Recognition System - Enterprise Edition",
            foreground="#888888",
            style="Status.TLabel"
        )
        footer_text.pack(side=tk.RIGHT)
        
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
        """Start or stop webcam-based face recognition"""
        if self.is_webcam_running:
            self.stop_webcam()
            return
        
        try:
            # Initialize webcam
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Webcam Error", "Could not open webcam. Please check your camera connection.")
                return
            
            self.is_webcam_running = True
            self.webcam_btn.config(text="Stop Webcam")
            self.result_label.config(text="Webcam active - Face recognition running")
            
            # Start webcam loop
            self.update_webcam_frame()
            
        except Exception as e:
            messagebox.showerror("Webcam Error", f"Error starting webcam: {str(e)}")
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
            self.webcam_btn.config(text="Start Webcam")
            self.result_label.config(text="Webcam stopped")
    
    def collect_faces(self):
        """Open the face collection interface"""
        try:
            # Stop webcam if running
            self.stop_webcam()
            
            # Create a popup window for name input
            name = self.show_name_input_dialog()
            if not name:
                return
                
            # Import the collect_faces module and run it
            import subprocess
            subprocess.Popen(["python", "collect_faces.py", name])
            messagebox.showinfo("Face Collection", f"Started face collection for {name}. Please follow the instructions in the new window.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start face collection: {str(e)}")
    
    def train_model(self):
        """Train the face recognition model"""
        try:
            # Stop webcam if running
            self.stop_webcam()
            
            # Show a message that training has started
            self.result_label.config(text="Training model... This may take a few minutes.")
            self.root.update()
            
            # Import the train_model module and run it
            import subprocess
            process = subprocess.Popen(["python", "train_model.py"], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                messagebox.showinfo("Training Complete", "Model training completed successfully!")
                # Reload the models
                self.load_models()
                self.update_status()
            else:
                error_msg = stderr.decode('utf-8')
                messagebox.showerror("Training Error", f"Failed to train model: {error_msg}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to train model: {str(e)}")
    
    def show_name_input_dialog(self):
        """Show a dialog to input person's name"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Name")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50,
                                    self.root.winfo_rooty() + 50))
        
        # Add padding
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        ttk.Label(frame, text="Enter the person's name:").pack(pady=(0, 10))
        
        # Entry
        name_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=name_var, width=30)
        entry.pack(pady=(0, 20))
        entry.focus_set()
        
        # Result
        result = [None]
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        def on_cancel():
            result[0] = None
            dialog.destroy()
            
        def on_ok():
            name = name_var.get().strip()
            if name:
                result[0] = name
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Name cannot be empty")
        
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT)
        
        # Handle Enter key
        dialog.bind("<Return>", lambda event: on_ok())
        dialog.bind("<Escape>", lambda event: on_cancel())
        
        # Wait for the dialog to close
        self.root.wait_window(dialog)
        return result[0]

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()