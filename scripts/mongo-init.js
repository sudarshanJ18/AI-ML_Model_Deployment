// MongoDB initialization script for face recognition application
// This script runs when the MongoDB container starts for the first time

// Switch to the face_recognition_db database
db = db.getSiblingDB('face_recognition_db');

// Create collections with proper indexes
db.createCollection('faces');
db.createCollection('recognition_logs');
db.createCollection('users');

// Create indexes for better performance
db.faces.createIndex({ "name": 1 });
db.faces.createIndex({ "created_at": -1 });
db.recognition_logs.createIndex({ "timestamp": -1 });
db.recognition_logs.createIndex({ "method": 1 });
db.users.createIndex({ "username": 1 }, { unique: true });

// Insert some sample data (optional)
db.faces.insertOne({
  name: "Sample Person",
  embedding: Array(512).fill(0.1), // Placeholder embedding
  image_path: "/uploads/sample.jpg",
  created_at: new Date()
});

print("MongoDB initialization completed successfully!");
