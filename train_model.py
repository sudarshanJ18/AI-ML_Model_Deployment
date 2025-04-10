import os
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
import cv2
import pickle
from utils import get_embedding
import tensorflow as tf

# Create models directory if it doesn't exist
os.makedirs("models", exist_ok=True)

# Path to the dataset
dataset_path = "dataset"

if not os.path.exists(dataset_path):
    print(f"Error: Dataset directory '{dataset_path}' does not exist.")
    print("Please run collect_faces.py first to create the dataset.")
    exit(1)

# Lists to store data
X, y = [], []

# Count files for progress tracking
total_files = len([f for f in os.listdir(dataset_path) if f.endswith(".jpg")])

if total_files == 0:
    print(f"Error: No images found in '{dataset_path}' directory.")
    print("Please run collect_faces.py first to collect face images.")
    exit(1)

print(f"Found {total_files} images. Processing...")
processed_files = 0

# Process each image in the dataset
for file in os.listdir(dataset_path):
    if file.endswith(".jpg"):
        try:
            image_path = os.path.join(dataset_path, file)
            face = cv2.imread(image_path)
            
            if face is None:
                print(f"Warning: Could not read image {file}")
                continue

            # Convert BGR to RGB (OpenCV loads as BGR)
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            
            # Get facial embedding
            embedding = get_embedding(face)
            
            # Extract person name from filename (format: name_number.jpg)
            name = file.split("_")[0]

            # Add data to lists
            X.append(embedding)
            y.append(name)

            # Update progress
            processed_files += 1
            if processed_files % 10 == 0 or processed_files == total_files:
                print(f"Processed {processed_files}/{total_files} images")

        except Exception as e:
            print(f"Error processing {file}: {e}")

# Check if we have data to train
if len(X) == 0:
    print("No valid face images could be processed. Training aborted.")
    exit(1)

# Convert lists to numpy arrays
X = np.array(X)
y = np.array(y)

print(f"Training model with {len(X)} face images from {len(set(y))} different people")

# Encode labels
le = LabelEncoder()
y = le.fit_transform(y)

# Save the label encoder
with open("models/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)
    print("Saved label encoder to models/label_encoder.pkl")

# Train SVM model
print("Training SVM model...")
svm_model = SVC(kernel='linear', probability=True)
svm_model.fit(X, y)

# Save the SVM model
with open("models/svm_model.pkl", "wb") as f:
    pickle.dump(svm_model, f)
    print("Saved SVM model to models/svm_model.pkl")

print("Training complete!")