import { ScrapingResult } from "@/types/types";

const API_BASE_URL = "http://localhost:8000/api";

export async function scrapeDocumentation(
  url: string
): Promise<ScrapingResult> {
  const response = await fetch(`${API_BASE_URL}/scrape`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Échec du scraping de la documentation");
  }

  // L'API renvoie un ID de tâche, on doit attendre que la tâche soit terminée
  const taskResponse = await response.json();
  const taskId = taskResponse.task_id;

  // On poll jusqu'à ce que la tâche soit terminée
  let status = await getScrapingStatus(taskId);
  while (status.status !== "completed") {
    if (status.status === "error") {
      throw new Error("Une erreur est survenue pendant le scraping");
    }

    // Attendre 2 secondes avant de vérifier à nouveau
    await new Promise((resolve) => setTimeout(resolve, 2000));
    status = await getScrapingStatus(taskId);
  }

  // Une fois terminé, récupérer le résultat
  return getScrapingResult(taskId);
}

export async function getScrapingStatus(
  taskId: string
): Promise<{ status: string; progress: number }> {
  const response = await fetch(`${API_BASE_URL}/progress/${taskId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Échec de la récupération du statut");
  }

  const data = await response.json();
  return {
    status: data.status,
    progress: data.progress,
  };
}

export async function getScrapingProgress(
  url: string
): Promise<{ processedPages: number; totalPages: number }> {
  // Cette fonction est utilisée par le hook useScraper pour récupérer la progression
  // Puisque nous n'avons pas le taskId direct ici, nous utilisons une approche différente
  // En réalité, cette fonction devrait être refactorisée pour utiliser le taskId
  const taskId = localStorage.getItem(
    `scraping_task_${encodeURIComponent(url)}`
  );

  if (!taskId) {
    return { processedPages: 0, totalPages: 1 };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/progress/${taskId}`);

    if (!response.ok) {
      return { processedPages: 0, totalPages: 1 };
    }

    const data = await response.json();
    return {
      processedPages: data.processed_pages || 0,
      totalPages: data.total_pages || 1,
    };
  } catch (error) {
    return { processedPages: 0, totalPages: 1 };
  }
}

export async function getScrapingResult(
  taskId: string
): Promise<ScrapingResult> {
  const response = await fetch(`${API_BASE_URL}/result/${taskId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Échec de la récupération du résultat");
  }

  const result = await response.json();
  return {
    url: result.url,
    content: result.content,
    status: result.status,
    timestamp: result.timestamp,
    taskId: result.task_id,
  };
}

export function getDownloadUrl(taskId: string): string {
  return `${API_BASE_URL}/download/${taskId}`;
}
