export interface ScrapingResult {
  url: string;
  content: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface QueueItem {
  url: string;
  baseUrl: string;
  basePath: string;
}

export interface ScrapingProgress {
  totalPages: number;
  processedPages: number;
  currentUrl: string;
}