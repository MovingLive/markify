export interface ScrapingResult {
  url: string;
  content: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface ScrapingStatus {
  isLoading: boolean;
  progress: number;
  error: string | null;
}