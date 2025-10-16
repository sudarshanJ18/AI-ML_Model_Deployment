#!/usr/bin/env python3
"""
MongoDB initialization script for Face Recognition Database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def init_database():
    """Initialize MongoDB database with collections and indexes"""
    
    # MongoDB connection
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.face_recognition_db
    
    try:
        # Create collections
        faces_collection = db.faces
        logs_collection = db.logs
        
        # Create indexes for better performance
        await faces_collection.create_index("name")
        await faces_collection.create_index("created_at")
        
        await logs_collection.create_index("timestamp")
        await logs_collection.create_index("method")
        await logs_collection.create_index("recognized_person")
        
        print("✅ Database initialized successfully!")
        print(f"✅ Created collections: faces, logs")
        print(f"✅ Created indexes for better performance")
        
        # Test connection
        await db.admin.command('ping')
        print("✅ Database connection test passed")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(init_database())
