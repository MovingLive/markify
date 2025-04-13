import { useState } from "react";
import { getScrapingStatus } from "../api/scraper";
import {
  ScrapingOptions,
  ScrapingResult,
  ScrapingStatus,
} from "../types/types";

// Règle: Utilisation de constantes pour les valeurs de configuration
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://tutu:8000/api";

/**
 * Hook personnalisé pour gérer le scraping de documentation.
 * L'expérience est transparente pour l'utilisateur avec téléchargement automatique.
 */
export function useScraper() {
  const [status, setStatus] = useState<ScrapingStatus>({
    isLoading: false,
    progress: 0,
    error: null,
  });
  const [result, setResult] = useState<ScrapingResult | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  /**
   * Lance le scraping d'une URL et gère la progression
   * Le téléchargement est automatique une fois terminé
   */
  const scrape = async (url: string, options: ScrapingOptions) => {
    setStatus({ isLoading: true, progress: 0, error: null });
    setResult(null);

    try {
      // Démarrer le scraping et obtenir le taskId
      const response = await fetch(`${API_BASE_URL}/scrape`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url,
          format: options.format,
          filename: options.filename,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Échec du scraping");
      }

      const data = await response.json();
      const newTaskId = data.task_id;
      setTaskId(newTaskId);

      // Démarrer le polling de progression
      const pollInterval = setInterval(async () => {
        try {
          const taskStatus = await getScrapingStatus(newTaskId);
          setStatus((prev) => ({
            ...prev,
            progress: taskStatus.progress,
          }));

          // Vérifier si la tâche est terminée
          if (taskStatus.status === "completed") {
            clearInterval(pollInterval);

            // Récupérer le résultat (cela déclenchera automatiquement le téléchargement)
            const response = await fetch(`${API_BASE_URL}/result/${newTaskId}`);
            const resultData = await response.json();

            // Créer un objet de résultat et l'assigner au state
            const scrapingResult: ScrapingResult = {
              taskId: newTaskId,
              url: resultData.url,
              content: resultData.content,
              status: resultData.status,
              timestamp: resultData.timestamp,
              format: resultData.format,
              filename: resultData.filename,
            };

            setResult(scrapingResult);
            setStatus((prev) => ({ ...prev, isLoading: false, progress: 100 }));

            // Déclencher automatiquement le téléchargement
            const link = document.createElement("a");
            link.href = `${API_BASE_URL}/download/${newTaskId}`;
            link.setAttribute("download", ""); // Le serveur gère le nom du fichier
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          } else if (taskStatus.status === "error") {
            clearInterval(pollInterval);
            throw new Error("Une erreur est survenue pendant le scraping");
          }
        } catch (error) {
          clearInterval(pollInterval);
          setStatus((prev) => ({
            ...prev,
            isLoading: false,
            error:
              error instanceof Error
                ? error.message
                : "Une erreur inattendue est survenue",
          }));
        }
      }, 2000); // Vérifier toutes les 2 secondes
    } catch (error) {
      setStatus((prev) => ({
        ...prev,
        isLoading: false,
        error:
          error instanceof Error
            ? error.message
            : "Une erreur inattendue est survenue",
      }));
    }
  };

  return {
    scrape,
    status,
    result,
    taskId,
  };
}
