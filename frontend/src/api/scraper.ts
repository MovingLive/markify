import { ScrapingResult, ScrapingStatus } from "@/types/types";

const API_BASE_URL = "http://localhost:8000/api";

/**
 * Déclenche le scraping d'une URL et suit sa progression.
 * Une fois terminé, télécharge automatiquement le fichier markdown.
 */
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
  taskId: string
): Promise<{ processedPages: number; totalPages: number }> {
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

  // Déclencher automatiquement le téléchargement du fichier
  downloadMarkdownFile(taskId);

  return {
    url: result.url,
    content: result.content,
    status: result.status,
    timestamp: result.timestamp,
    taskId: result.task_id,
  };
}

/**
 * Télécharge le fichier markdown directement dans le navigateur
 * sans avoir besoin de cliquer sur un bouton.
 */
export function downloadMarkdownFile(taskId: string): void {
  const downloadUrl = `${API_BASE_URL}/download/${taskId}`;

  // Créer un lien invisible et le cliquer pour déclencher le téléchargement
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.setAttribute("download", ""); // Le serveur gère le nom du fichier
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
