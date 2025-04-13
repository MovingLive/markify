export interface ScrapingResult {
  url: string;
  content: string;
  status: 'success' | 'error';
  timestamp: string;
  taskId?: string;  // ID de la tâche pour le téléchargement
  useCrawl4ai?: boolean; // Si true, a utilisé l'API crawl4ai
}

export interface ScrapingStatus {
  isLoading: boolean;
  progress: number;
  error: string | null;
}
