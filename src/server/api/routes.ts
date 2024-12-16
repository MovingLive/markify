import express from 'express';
import { DocumentationScraper } from '../services/documentationScraper';

const router = express.Router();

router.post('/scrape', async (req, res) => {
  const { url } = req.body;
  
  if (!url) {
    return res.status(400).json({ error: 'URL is required' });
  }

  try {
    const scraper = new DocumentationScraper();
    const content = await scraper.scrape(url);
    
    res.json({
      url,
      content,
      status: 'success',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    res.status(500).json({
      error: 'Failed to scrape documentation',
      details: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

router.get('/progress', (req, res) => {
  // In a real application, you'd want to store the scraper instance
  // and retrieve the actual progress. This is just a placeholder.
  res.json({
    progress: 50,
    status: 'processing',
  });
});

export default router;