from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Prompt(BaseModel):
    id: Optional[int] = None
    title: str
    category: str
    scenario: str
    platform: str
    content: str
    output_type: str
    preview_images: str = "[]"
    trend_score: float = 50.0
    usage_count: int = 0
    source: str = "crawler"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Trend(BaseModel):
    id: Optional[int] = None
    category: str
    keyword: str
    heat: float = 0.0
    source: str = "builtin"
    created_at: Optional[str] = None

class ImportLog(BaseModel):
    id: Optional[int] = None
    filename: str
    row_count: int = 0
    trends_extracted: int = 0
    created_at: Optional[str] = None

class GenerateRequest(BaseModel):
    category: str
    scenario: str
    platform: str
    output_type: str
    description: str = ""

class GenerateResponse(BaseModel):
    prompt: str
    explanation: str = ""

class PromptListResponse(BaseModel):
    items: List[Prompt]
    total: int
    page: int
    page_size: int
