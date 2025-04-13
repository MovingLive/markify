export interface ScrapingResult {
  url: string;
  content: string;
  status: "success" | "error";
  timestamp: string;
  taskId?: string; // ID de la tâche pour le téléchargement
  format?: "single_file" | "zip_files";
  filename?: string;
}

export interface ScrapingStatus {
  isLoading: boolean;
  progress: number;
  error: string | null;
}

export interface ScrapingOptions {
  format: "single_file" | "zip_files";
  filename: string;
}
