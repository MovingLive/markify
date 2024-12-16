from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .models.schemas import ScrapeRequest, ScrapingResult, ScrapingProgress
from .services.documentation_scraper import DocumentationScraper

# Store active scraping jobs
active_scrapers: dict[str, DocumentationScraper] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cleanup on shutdown
    yield
    active_scrapers.clear()

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/scrape")
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

@app.get("/api/progress/{url}")
async def get_progress(url: str) -> ScrapingProgress:
    """Get progress for a specific scraping job."""
    scraper = active_scrapers.get(url)
    if not scraper:
        raise HTTPException(status_code=404, detail="Scraping job not found")
    return scraper.get_progress()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)