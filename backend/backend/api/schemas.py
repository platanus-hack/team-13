from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

# Input Schemas
class TextEventCreate(BaseModel):
    message: str = Field(..., description="Text message content")
    type: str = Field(default="form_input", description="Type of text event")

class MouseEventCreate(BaseModel):
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")
    viewport_x: int = Field(..., description="Viewport width")
    viewport_y: int = Field(..., description="Viewport height")

class NetworkEventCreate(BaseModel):
    headers: Dict = Field(..., description="Request headers")
    method: str = Field(..., description="HTTP method")
    body: Dict = Field(..., description="Request body")
    cookies: Dict = Field(..., description="Request cookies")
    url: str = Field(..., description="Request URL")
    status_code: int = Field(..., description="Response status code")

# Response Schemas
class TextEventResponse(BaseModel):
    id: int
    message: str
    type: str
    is_malicious: bool | None = None
    confidence_score: float | None = None
    created_at: datetime | None = None
    blocked_at: datetime | None = None
    domain: str | None = None
    ip_address: str | None = None

class DecisionResponse(BaseModel):
    ip_address: str
    is_malicious: bool
    event_id: int
    confidence_score: float | None = None
    type: str | None = None

class BlockResponse(BaseModel):
    success: bool
    message: str
    ip_address: str | None = None
    domain: str | None = None
