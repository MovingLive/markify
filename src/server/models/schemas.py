from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class ScrapeRequest(BaseModel):
    url: HttpUrl

class ScrapingProgress(BaseModel):
    total_pages: int
    processed_pages: int
    current_url: Optional[str] = None

class ScrapingResult(BaseModel):
    url: str
    content: str
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True