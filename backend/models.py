from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Face(BaseModel):
    name: str
    embedding: List[float]
    image_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RecognitionLog(BaseModel):
    method: str  # "camera" or "upload"
    recognized_person: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)