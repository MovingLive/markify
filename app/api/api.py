from fastapi import APIRouter, HTTPException, status
from app.services.documentation_scraper import DocumentationScraper

api_router = APIRouter()


# health endPoint
@api_router.get("/health")
async def health():
    return {"status": "ok"}


@api_router.post("/scrape")
async def scrape_documentation(request: ScrapeRequest) -> str:
    """Start scraping documentation from the given URL."""
    return "Hello World"
