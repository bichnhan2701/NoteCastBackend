# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class ChunkResult(BaseModel):
    start: float
    end: float
    text: str

class TranscriptionResponse(BaseModel):
    text: str
    duration_seconds: float
    model: str
    processing_time_seconds: float
    chunks: List[ChunkResult]
    playback_url: Optional[str] = None
