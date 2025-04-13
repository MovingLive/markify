import { ScrapingResult, ScrapingStatus } from '@/types/types';

const API_BASE_URL = 'http://localhost:3000/api';

export async function scrapeDocumentation(url: string): Promise<ScrapingResult> {
  const response = await fetch(`${API_BASE_URL}/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to scrape documentation');
  }

  return response.json();
}

export async function getScrapingProgress(url: string): Promise<ScrapingStatus> {
  const response = await fetch(`${API_BASE_URL}/progress/${encodeURIComponent(url)}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to get scraping progress');
  }

  return response.json();
}