import { useState, useEffect } from 'react';
import { ScrapingResult, ScrapingStatus } from '../types/types';
import { scrapeDocumentation, getScrapingProgress } from '../api/scraper';

export function useScraper() {
  const [status, setStatus] = useState<ScrapingStatus>({
    isLoading: false,
    progress: 0,
    error: null,
  });
  const [result, setResult] = useState<ScrapingResult | null>(null);

  const scrape = async (url: string) => {
    setStatus({ isLoading: true, progress: 0, error: null });
    setResult(null);

    try {
      // Start progress polling
      const pollInterval = setInterval(async () => {
        try {
          const progress = await getScrapingProgress(url);
          setStatus(prev => ({
            ...prev,
            progress: Math.round((progress.processedPages / progress.totalPages) * 100),
          }));
        } catch (error) {
          // Ignore polling errors
        }
      }, 1000);

      // Start scraping
      const scrapingResult = await scrapeDocumentation(url);
      setResult(scrapingResult);
      
      // Cleanup
      clearInterval(pollInterval);
      setStatus(prev => ({ ...prev, isLoading: false, progress: 100 }));
    } catch (error) {
      setStatus(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'An unexpected error occurred',
      }));
    }
  };

  return {
    scrape,
    status,
    result,
  };
}