import { useState } from 'react';
import { ScrapingResult, ScrapingStatus } from '../types/types';
import { 
  scrapeDocumentation, 
  getScrapingProgress, 
  getScrapingStatus
} from '../api/scraper';

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
   * 
   * @param url URL à scraper
   * @param useCrawl4ai Si true, utilise l'API crawl4ai au lieu du scraper standard
   */
  const scrape = async (url: string, useCrawl4ai: boolean = false) => {
    setStatus({ isLoading: true, progress: 0, error: null });
    setResult(null);

    try {
      // Démarrer le scraping et obtenir le taskId
      const response = await fetch('http://localhost:8000/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, use_crawl4ai: useCrawl4ai }),
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Échec du scraping');
      }
      
      const data = await response.json();
      const newTaskId = data.task_id;
      setTaskId(newTaskId);

      // Démarrer le polling de progression
      const pollInterval = setInterval(async () => {
        try {
          const taskStatus = await getScrapingStatus(newTaskId);
          setStatus(prev => ({
            ...prev,
            progress: taskStatus.progress,
          }));

          // Vérifier si la tâche est terminée
          if (taskStatus.status === 'completed') {
            clearInterval(pollInterval);
            
            // Récupérer le résultat (cela déclenchera automatiquement le téléchargement)
            const response = await fetch(`http://localhost:8000/api/result/${newTaskId}`);
            const resultData = await response.json();
            
            // Créer un objet de résultat et l'assigner au state
            const scrapingResult: ScrapingResult = {
              taskId: newTaskId,
              url: resultData.url,
              content: resultData.content,
              status: resultData.status,
              timestamp: resultData.timestamp,
              useCrawl4ai: useCrawl4ai
            };
            
            setResult(scrapingResult);
            setStatus(prev => ({ ...prev, isLoading: false, progress: 100 }));
            
            // Déclencher automatiquement le téléchargement
            const link = document.createElement('a');
            link.href = `http://localhost:8000/api/download/${newTaskId}`;
            link.setAttribute('download', '');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
          } else if (taskStatus.status === 'error') {
            clearInterval(pollInterval);
            throw new Error('Une erreur est survenue pendant le scraping');
          }
        } catch (error) {
          clearInterval(pollInterval);
          setStatus(prev => ({
            ...prev,
            isLoading: false,
            error: error instanceof Error ? error.message : 'Une erreur inattendue est survenue',
          }));
        }
      }, 2000); // Vérifier toutes les 2 secondes
      
    } catch (error) {
      setStatus(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Une erreur inattendue est survenue',
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
