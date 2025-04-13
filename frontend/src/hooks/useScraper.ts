import { useState } from "react";
import {
  getDownloadUrl,
  getScrapingResult,
  getScrapingStatus,
} from "../api/scraper";
import { ScrapingResult, ScrapingStatus } from "../types/types";

export function useScraper() {
  const [status, setStatus] = useState<ScrapingStatus>({
    isLoading: false,
    progress: 0,
    error: null,
  });
  const [result, setResult] = useState<ScrapingResult | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  const scrape = async (url: string) => {
    setStatus({ isLoading: true, progress: 0, error: null });
    setResult(null);

    try {
      // Démarrer le scraping et obtenir le taskId
      const response = await fetch("http://localhost:8000/api/scrape", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Échec du scraping");
      }

      const data = await response.json();
      const newTaskId = data.task_id;
      setTaskId(newTaskId);

      // Sauvegarder le taskId dans localStorage pour la récupération de progression
      localStorage.setItem(
        `scraping_task_${encodeURIComponent(url)}`,
        newTaskId
      );

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

            // Récupérer le résultat
            const scrapingResult = await getScrapingResult(newTaskId);
            scrapingResult.taskId = newTaskId; // S'assurer que le taskId est inclus
            setResult(scrapingResult);
            setStatus((prev) => ({ ...prev, isLoading: false, progress: 100 }));
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

  const downloadResult = () => {
    if (taskId) {
      const downloadUrl = getDownloadUrl(taskId);
      window.open(downloadUrl, "_blank");
    }
  };

  return {
    scrape,
    downloadResult,
    status,
    result,
    taskId,
  };
}
