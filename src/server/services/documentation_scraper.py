import asyncio
import httpx
from typing import Set, List, Dict
from datetime import datetime

from ..models.schemas import ScrapingProgress, ScrapingResult
from ..utils.url_utils import normalize_url, get_base_info, is_valid_next_url
from .html_processor import HtmlProcessor

class DocumentationScraper:
    def __init__(self):
        self.visited: Set[str] = set()
        self.queue: List[Dict[str, str]] = []
        self.markdown_contents: List[str] = []
        self.html_processor = HtmlProcessor()
        self.progress = ScrapingProgress(
            total_pages=0,
            processed_pages=0,
            current_url=None
        )

    async def scrape(self, start_url: str) -> ScrapingResult:
        """Scrape documentation starting from the given URL."""
        normalized_start_url = normalize_url(str(start_url))
        base_url, base_path = get_base_info(normalized_start_url)

        self.queue.append({
            'url': normalized_start_url,
            'base_url': base_url,
            'base_path': base_path
        })
        self.progress.total_pages = 1

        async with httpx.AsyncClient() as client:
            while self.queue:
                current = self.queue.pop(0)
                url = current['url']
                normalized_url = normalize_url(url)

                if normalized_url in self.visited:
                    continue

                self.visited.add(normalized_url)
                self.progress.current_url = normalized_url
                self.progress.processed_pages += 1

                try:
                    response = await client.get(normalized_url)
                    response.raise_for_status()
                    html = response.text

                    # Process the page
                    main_content = self.html_processor.extract_main_content(html)
                    markdown = self.html_processor.convert_to_markdown(main_content)
                    processed_markdown = self.html_processor.process_markdown(markdown)

                    if processed_markdown.strip():
                        self.markdown_contents.append(processed_markdown)

                    # Extract and queue new links
                    links = self.html_processor.extract_links(html, url)
                    for link in links:
                        if (link not in self.visited and 
                            is_valid_next_url(link, current['base_url'], current['base_path'])):
                            self.queue.append({
                                'url': link,
                                'base_url': current['base_url'],
                                'base_path': current['base_path']
                            })
                            self.progress.total_pages += 1

                except Exception as e:
                    print(f"Error processing {normalized_url}: {str(e)}")

        return ScrapingResult(
            url=start_url,
            content='\n\n---\n\n'.join(self.markdown_contents),
            status='success',
            timestamp=datetime.now()
        )

    def get_progress(self) -> ScrapingProgress:
        """Get current scraping progress."""
        return self.progress