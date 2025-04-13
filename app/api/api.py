from fastapi import APIRouter, HTTPException, status
from app.models import ScrapeRequest, ScrapingResult
from app.services.documentation_scraper import DocumentationScraper

api_router = APIRouter()


# health endPoint
@api_router.get("/health")
async def health():
    return {"status": "ok"}


@api_router.post("/scrape")
async def scrape_documentation(request: ScrapeRequest) -> ScrapingResult:
    """Start scraping documentation from the given URL."""
    try:
        scraper = DocumentationScraper()
        active_scrapers[str(request.url)] = scraper
        result = await scraper.scrape(str(request.url))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        active_scrapers.pop(str(request.url), None)
