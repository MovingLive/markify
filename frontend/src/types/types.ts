export interface ScrapingResult {
  url: string;
  content: string;
  status: "success" | "error";
  timestamp: string;
  taskId?: string; // ID de la tâche pour le téléchargement
}

export interface ScrapingStatus {
  isLoading: boolean;
  progress: number;
  error: string | null;
}
