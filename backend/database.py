from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from datetime import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)

# MongoDB connection string
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb-service:27017/face_recognition_db")

# Database client
client = AsyncIOMotorClient(MONGODB_URL)
db = client.face_recognition_db

# Collections
users_collection = db.users
recognition_logs_collection = db.recognition_logs
faces_collection = db.faces

async def init_db():
    """Initialize database with indexes and default data if needed"""
    try:
        # Create indexes
        await users_collection.create_index("username", unique=True)
        await recognition_logs_collection.create_index("timestamp")
        await faces_collection.create_index("person_name")
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def add_user(user_data):
    """Add a new user to the database"""
    user_data["created_at"] = datetime.utcnow()
    result = await users_collection.insert_one(user_data)
    return result.inserted_id

async def get_user_by_username(username):
    """Get user by username"""
    return await users_collection.find_one({"username": username})

async def update_user(user_id, update_data):
    """Update user information"""
    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

async def log_recognition(user_id, image_filename, faces_detected, recognized_faces):
    """Log a face recognition attempt"""
    log_entry = {
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "image_filename": image_filename,
        "faces_detected": faces_detected,
        "recognized_faces": recognized_faces
    }
    result = await recognition_logs_collection.insert_one(log_entry)
    return result.inserted_id

async def save_face_embedding(person_name, embedding, image_path=None):
    """Save a face embedding to the database"""
    face_entry = {
        "person_name": person_name,
        "embedding": embedding.tolist(),  # Convert numpy array to list for storage
        "image_path": image_path,
        "created_at": datetime.utcnow()
    }
    result = await faces_collection.insert_one(face_entry)
    return result.inserted_id

async def get_face_embeddings(person_name=None):
    """Get face embeddings, optionally filtered by person name"""
    query = {}
    if person_name:
        query["person_name"] = person_name
    
    cursor = faces_collection.find(query)
    return await cursor.to_list(length=None)

async def get_recognition_logs(user_id=None, limit=50):
    """Get recognition logs, optionally filtered by user ID"""
    query = {}
    if user_id:
        query["user_id"] = user_id
    
    cursor = recognition_logs_collection.find(query).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=None)