from fastapi import APIRouter, HTTPException, status
from h11 import Request

api_router = APIRouter()


# health endPoint
@api_router.get("/health")
async def health():
    return {"status": "ok"}


@api_router.post("/scrape")
async def scrape_documentation(request: Request) -> str:
    """Start scraping documentation from the given URL."""
    return "Hello World"
