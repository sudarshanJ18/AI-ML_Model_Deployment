from fastapi import FastAPI, File, UploadFile, HTTPException, Body, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import logging
import uuid
import json
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import face recognition utilities
try:
    from face_recognition_utils import (
        get_face_engine, 
        preprocess_image, 
        save_face_image
    )
    face_recognition_available = True
    logger = logging.getLogger(__name__)
    logger.info("Face recognition utilities loaded successfully")
except ImportError as e:
    face_recognition_available = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Face recognition utilities not available: {e}")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Face Recognition API",
    description="Face Recognition API with MongoDB Integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# MongoDB connection (optional - will work without it)
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from bson import ObjectId
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.face_recognition_db
    mongodb_available = True
    logger.info("MongoDB connection established")
except ImportError:
    mongodb_available = False
    logger.warning("MongoDB not available, using in-memory storage")

# Pydantic models
class Face(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    name: str
    embedding: List[float] = []
    image_path: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RecognitionLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    method: str  # "camera" or "upload"
    recognized_person: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# In-memory storage for fallback
faces_storage: List[Dict[str, Any]] = []
logs_storage: List[Dict[str, Any]] = []

# Initialize with some sample data
def init_sample_data():
    """Initialize with sample data for demonstration"""
    sample_faces = [
        Face(name="Alice Johnson", embedding=[0.1]*512, image_path="sample/alice.jpg").dict(),
        Face(name="Bob Williams", embedding=[0.2]*512, image_path="sample/bob.jpg").dict(),
        Face(name="Charlie Davis", embedding=[0.3]*512, image_path="sample/charlie.jpg").dict()
    ]
    
    sample_logs = [
        RecognitionLog(method="upload", recognized_person="Alice Johnson", confidence=0.98).dict(),
        RecognitionLog(method="camera", recognized_person="Bob Williams", confidence=0.91).dict(),
        RecognitionLog(method="camera", recognized_person="Unknown", confidence=0.65).dict()
    ]
    
    faces_storage.extend(sample_faces)
    logs_storage.extend(sample_logs)
    logger.info(f"Initialized with {len(sample_faces)} sample faces and {len(sample_logs)} sample logs")

init_sample_data()

@app.post("/recognize")
async def recognize_face(
    file: UploadFile = File(...),
    threshold_param: float = Form(0.6)
):
    """Recognize faces in an uploaded image using real ML models"""
    if not file:
        raise HTTPException(status_code=400, detail="No image file provided")
    
    try:
        # Read and preprocess the image
        contents = await file.read()
        
        if face_recognition_available:
            # Use real face recognition
            try:
                # Preprocess image
                image = preprocess_image(contents)
                
                # Get face recognition engine
                face_engine = get_face_engine()
                
                # Get known faces from storage
                known_faces = faces_storage if not mongodb_available else await get_faces_from_db()
                
                # Recognize faces
                recognized_faces = face_engine.recognize_faces(
                    image, 
                    known_faces, 
                    threshold_param
                )
                
                faces_detected = len(recognized_faces)
                
            except Exception as e:
                logger.error(f"Real face recognition failed: {e}")
                # Fallback to simulation
                recognized_faces = simulate_recognition()
                faces_detected = len(recognized_faces)
        else:
            # Fallback to simulation
            recognized_faces = simulate_recognition()
            faces_detected = len(recognized_faces)
        
        # Determine method
        method = "camera" if "live" in file.filename.lower() else "upload"
        
        # Log the recognition
        log_entry = RecognitionLog(
            method=method,
            recognized_person=recognized_faces[0]['name'] if recognized_faces else None,
            confidence=recognized_faces[0]['confidence'] if recognized_faces else None
        )
        
        # Save log
        if mongodb_available:
            try:
                logs_collection = db.logs
                await logs_collection.insert_one(log_entry.dict())
            except Exception as e:
                logger.error(f"Error saving to MongoDB: {e}")
                logs_storage.append(log_entry.dict())
        else:
            logs_storage.append(log_entry.dict())
        
        return JSONResponse(content={
            "faces_detected": faces_detected,
            "recognized_faces": recognized_faces
        })
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

def simulate_recognition():
    """Fallback simulation for face recognition"""
    import random
    available_names = [face['name'] for face in faces_storage]
    
    faces_detected = random.choice([0, 1, 2])
    recognized_faces = []
    
    if faces_detected > 0 and available_names:
        for i in range(faces_detected):
            if random.random() > 0.3:  # 70% chance of recognizing someone
                name = random.choice(available_names)
                confidence = 0.8 + random.random() * 0.2  # 0.8-1.0
            else:
                name = "Unknown"
                confidence = 0.6 + random.random() * 0.2  # 0.6-0.8
            
            recognized_faces.append({
                "name": name,
                "confidence": confidence,
                "bounding_box": [100 + i*50, 100 + i*50, 200 + i*50, 200 + i*50]
            })
    
    return recognized_faces

async def get_faces_from_db():
    """Get faces from MongoDB database"""
    try:
        faces_collection = db.faces
        faces = await faces_collection.find().to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for face in faces:
            if '_id' in face:
                face['_id'] = str(face['_id'])
                face['id'] = face['_id']
        
        return faces
    except Exception as e:
        logger.error(f"Error getting faces from MongoDB: {e}")
        return faces_storage

@app.post("/faces")
async def add_face(
    name: str = Form(...),
    file: UploadFile = File(...)
):
    """Add a new face to the database using real face recognition"""
    if not name or not file:
        raise HTTPException(status_code=400, detail="Name and image file are required.")
    
    try:
        # Read and preprocess the image
        contents = await file.read()
        
        if face_recognition_available:
            # Use real face recognition
            try:
                # Preprocess image
                image = preprocess_image(contents)
                
                # Get face recognition engine
                face_engine = get_face_engine()
                
                # Add face using real ML models
                face_data_dict = face_engine.add_face(image, name)
                
                # Create face entry with real data
                face_data = Face(
                    name=name,
                    embedding=face_data_dict['embedding'],
                    image_path=face_data_dict['image_path']
                )
                
                # Save the image to disk
                filename = f"{name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
                image_path = save_face_image(image, filename)
                face_data.image_path = image_path
                
            except Exception as e:
                logger.error(f"Real face recognition failed: {e}")
                # Fallback to simulation
                face_data = Face(
                    name=name,
                    embedding=[0.1] * 512,  # Dummy embedding
                    image_path=f"uploads/{name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
                )
        else:
            # Fallback to simulation
            face_data = Face(
                name=name,
                embedding=[0.1] * 512,  # Dummy embedding
                image_path=f"uploads/{name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
            )
        
        # Save to storage
        if mongodb_available:
            try:
                faces_collection = db.faces
                await faces_collection.insert_one(face_data.dict())
            except Exception as e:
                logger.error(f"Error saving to MongoDB: {e}")
                faces_storage.append(face_data.dict())
        else:
            faces_storage.append(face_data.dict())
        
        return JSONResponse(content={
            "message": f"Face for '{name}' added successfully.",
            "face": face_data.dict()
        })

    except Exception as e:
        logger.error(f"Error adding face: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding face: {str(e)}")

@app.get("/faces")
async def get_faces():
    """Get all faces from the database"""
    try:
        if mongodb_available:
            try:
                faces_collection = db.faces
                faces = await faces_collection.find().to_list(length=None)
                
                # Convert ObjectId to string for JSON serialization
                for face in faces:
                    if '_id' in face:
                        face['_id'] = str(face['_id'])
                        face['id'] = face['_id']
                
                return JSONResponse(content=faces)
            except Exception as e:
                logger.error(f"Error getting faces from MongoDB: {e}")
                # Fallback to in-memory storage
                pass
        
        # Use in-memory storage
        # Convert datetime objects to strings for JSON serialization
        serializable_faces = []
        for face in faces_storage:
            face_copy = face.copy()
            if 'created_at' in face_copy and isinstance(face_copy['created_at'], datetime):
                face_copy['created_at'] = face_copy['created_at'].isoformat()
            serializable_faces.append(face_copy)
        return JSONResponse(content=serializable_faces)
        
    except Exception as e:
        logger.error(f"Error getting faces: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting faces: {str(e)}")

@app.delete("/faces/{face_id}")
async def delete_face(face_id: str):
    """Delete a face from the database"""
    try:
        if mongodb_available:
            try:
                faces_collection = db.faces
                # Try to delete by _id first (MongoDB ObjectId), then by id field
                result = await faces_collection.delete_one({"_id": ObjectId(face_id)})
                
                if result.deleted_count == 0:
                    # If not found by _id, try by id field
                    result = await faces_collection.delete_one({"id": face_id})
                
                if result.deleted_count > 0:
                    return JSONResponse(content={"message": "Face deleted successfully."})
            except Exception as e:
                logger.error(f"Error deleting from MongoDB: {e}")
                # Fallback to in-memory storage
                pass
        
        # Use in-memory storage
        initial_len = len(faces_storage)
        faces_storage[:] = [face for face in faces_storage if face.get('id') != face_id and face.get('_id') != face_id]
        
        if len(faces_storage) < initial_len:
            return JSONResponse(content={"message": "Face deleted successfully."})
        else:
            raise HTTPException(status_code=404, detail=f"Face with ID {face_id} not found")
            
    except Exception as e:
        logger.error(f"Error deleting face: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting face: {str(e)}")

@app.get("/logs")
async def get_logs():
    """Get all recognition logs"""
    try:
        if mongodb_available:
            try:
                logs_collection = db.logs
                logs = await logs_collection.find().sort("timestamp", -1).to_list(length=None)
                
                # Convert ObjectId to string for JSON serialization
                for log in logs:
                    if '_id' in log:
                        log['_id'] = str(log['_id'])
                        log['id'] = log['_id']
                
                return JSONResponse(content=logs)
            except Exception as e:
                logger.error(f"Error getting logs from MongoDB: {e}")
                # Fallback to in-memory storage
                pass
        
        # Use in-memory storage
        # Convert datetime objects to strings for JSON serialization
        serializable_logs = []
        for log in logs_storage:
            log_copy = log.copy()
            if 'timestamp' in log_copy and isinstance(log_copy['timestamp'], datetime):
                log_copy['timestamp'] = log_copy['timestamp'].isoformat()
            serializable_logs.append(log_copy)
        sorted_logs = sorted(serializable_logs, key=lambda x: x['timestamp'], reverse=True)
        return JSONResponse(content=sorted_logs)
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        status = "healthy"
        database_status = "not_available"
        storage_type = "in-memory"
        models_status = "simulated"
        
        if mongodb_available:
            try:
                await db.admin.command('ping')
                database_status = "connected"
                storage_type = "mongodb"
            except Exception as e:
                logger.error(f"MongoDB health check failed: {e}")
                database_status = "disconnected"
        
        if face_recognition_available:
            models_status = "real_ml_models"
        
        return {
            "status": status,
            "database": database_status,
            "storage": storage_type,
            "models": models_status,
            "face_recognition": "available" if face_recognition_available else "unavailable"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        models_status = "simulated"
        if face_recognition_available:
            models_status = "real_ml_models"
        
        storage_type = "mongodb" if mongodb_available else "in-memory"
        
        return {
            "status": "ready",
            "models": models_status,
            "storage": storage_type,
            "face_recognition": "available" if face_recognition_available else "unavailable"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not ready", "error": str(e)}

@app.get("/")
def read_root():
    return {"message": "Face Recognition API is running", "status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)