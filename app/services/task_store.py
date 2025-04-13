"""Module de stockage partagé pour les tâches de scraping."""
from typing import Dict, Optional

# Dictionnaire global pour suivre la progression des tâches de scraping
scraping_tasks: Dict[str, Dict] = {}


def get_task_status(task_id: str) -> Dict:
    """Récupère le statut d'une tâche de scraping."""
    if task_id not in scraping_tasks:
        return {"status": "not_found"}
    
    return scraping_tasks[task_id]


def get_markdown_content(task_id: str) -> Optional[str]:
    """Récupère le contenu Markdown d'une tâche de scraping terminée."""
    if task_id not in scraping_tasks or scraping_tasks[task_id]["status"] != "completed":
        return None
    
    return scraping_tasks[task_id].get("markdown_content")