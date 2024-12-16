import { Router } from 'express';
import { scrapeDocumentation, getScrapingProgress } from '../controllers/scraper.controller';
import { validateUrl } from '../middleware/validateUrl';

const router = Router();

router.post('/scrape', validateUrl, scrapeDocumentation);
router.get('/progress/:url', getScrapingProgress);

export default router;