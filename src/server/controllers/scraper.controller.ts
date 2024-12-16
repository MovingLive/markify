import { Request, Response } from 'express';
import { DocumentationScraper } from '../services/documentationScraper';
import { ScraperManager } from '../services/scraperManager';

const scraperManager = new ScraperManager();

export const scrapeDocumentation = async (req: Request, res: Response) => {
  const { url } = req.body;

  try {
    const scraper = new DocumentationScraper();
    scraperManager.addScraper(url, scraper);
    
    const result = await scraper.scrape(url);
    
    res.json({
      url,
      content: result,
      status: 'success',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    res.status(500).json({
      error: 'Failed to scrape documentation',
      details: error instanceof Error ? error.message : 'Unknown error',
    });
  } finally {
    scraperManager.removeScraper(url);
  }
};

export const getScrapingProgress = (req: Request, res: Response) => {
  const { url } = req.params;
  const scraper = scraperManager.getScraper(url);

  if (!scraper) {
    return res.status(404).json({ error: 'Scraping job not found' });
  }

  res.json(scraper.getProgress());
};