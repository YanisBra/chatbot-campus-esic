"""
Pydantic API Schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user query text")
    session_id: str = Field(default="default_session", description="Unique conversation session ID")
    client_id: str = Field(default="default_client", description="Client identifier for rate limiting")
    user_profile: Optional[Dict[str, Any]] = Field(default=None, description="Optional profile context (e.g. formation, annee)")
    source: str = Field(default="web", description="'web', 'mobile', or 'borne_iot'")
    language: Optional[str] = Field(default=None, description="'fr', 'en', or 'es'")

class FeedbackRequest(BaseModel):
    interaction_id: Optional[int] = None
    session_id: Optional[str] = None
    rating: int = Field(..., description="1 for thumbs up, -1 for thumbs down")
    comment: Optional[str] = None

class KnowledgeItemCreate(BaseModel):
    category: str
    question: str
    answer: str
    keywords: Optional[str] = ""

class KioskHeartbeatRequest(BaseModel):
    kiosk_id: str
    battery: int = 100
    mode: str = "visiteur"

class BadgeScanRequest(BaseModel):
    card_id: str

class NotificationCreate(BaseModel):
    title: str
    message: str
    category: str
    priority: str = "info"
