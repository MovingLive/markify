import { DocumentationScraper } from './documentationScraper';

export class ScraperManager {
  private scrapers: Map<string, DocumentationScraper>;

  constructor() {
    this.scrapers = new Map();
  }

  addScraper(url: string, scraper: DocumentationScraper) {
    this.scrapers.set(url, scraper);
  }

  getScraper(url: string) {
    return this.scrapers.get(url);
  }

  removeScraper(url: string) {
    this.scrapers.delete(url);
  }

  cleanup() {
    this.scrapers.clear();
  }
}