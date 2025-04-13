"""Service de scraping de documentation web vers markdown."""
import os
import asyncio
import uuid
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urldefrag, urljoin, urlparse

import aiohttp
import html2text
from bs4 import BeautifulSoup

# Dictionnaire global pour suivre la progression des tâches de scraping
scraping_tasks: Dict[str, Dict] = {}


def normalize_url(url: str) -> str:
    """Normalise l'URL en supprimant le fragment et la barre oblique finale."""
    url, _ = urldefrag(url)
    if url.endswith("/"):
        url = url[:-1]
    return url


async def process_url(
    url: str,
    session: aiohttp.ClientSession,
    base_netloc: str,
    base_path: str,
    visited: Set[str],
    url_to_markdown: Dict[str, str],
    total_urls: List[str],
    task_id: str,
) -> List[str]:
    """Traite une URL spécifique et extrait son contenu en markdown."""
    new_urls_to_process = []
    
    try:
        async with session.get(url, timeout=30) as response:
            if response.status != 200:
                return new_urls_to_process
                
            html_content = await response.text()
            soup = BeautifulSoup(html_content, "html.parser")

            # Extraire le contenu principal
            main_content = soup.find("main", {"id": "article-contents"})
            if main_content is None:
                main_content = soup.find("div", {"class": "markdown-body"})
                if main_content is None:
                    main_content = soup

            # Convertir le contenu principal en Markdown
            html_main_content = str(main_content)
            converter = html2text.HTML2Text()
            converter.ignore_links = False
            markdown = converter.handle(html_main_content)

            # Supprimer tout avant le premier titre de niveau 1
            lines = markdown.split("\n")
            start_index = None
            for i, line in enumerate(lines):
                if line.startswith("# "):
                    start_index = i
                    break
            
            if start_index is not None:
                markdown = "\n".join(lines[start_index:])
                # Stocker le contenu Markdown associé à l'URL
                url_to_markdown[url] = markdown

            # Trouver tous les liens et les ajouter à la file d'attente
            for link in main_content.find_all("a", href=True):
                href = link["href"]
                next_url = urljoin(url, href)
                parsed_next_url = urlparse(next_url)
                if parsed_next_url.netloc != base_netloc:
                    continue
                next_url = normalize_url(next_url)
                if not parsed_next_url.path.startswith(base_path):
                    continue
                if next_url not in visited:
                    new_urls_to_process.append(next_url)
                    total_urls.append(next_url)

        # Mettre à jour la progression
        scraping_tasks[task_id]["processed_pages"] += 1
        scraping_tasks[task_id]["total_pages"] = len(total_urls)
        scraping_tasks[task_id]["progress"] = min(
             100, int((scraping_tasks[task_id]["processed_pages"] / max(len(total_urls), 1)) * 100)
        )
        
    except Exception as e:
        print(f"Échec du traitement de {url}: {e}")
        
    return new_urls_to_process


async def crawl_and_collect_async(start_url: str, task_id: str) -> Dict[str, str]:
    """
    Version asynchrone de la fonction de crawl qui parcourt la documentation
    et collecte le contenu Markdown de chaque page.
    """
    # Initialisation des structures de données
    visited = set()
    queue = deque([start_url])
    total_urls = [start_url]
    base_netloc = urlparse(start_url).netloc
    base_path = urlparse(start_url).path
    url_to_markdown = {}

    # Initialiser la progression
    scraping_tasks[task_id]["start_time"] = datetime.now().isoformat()
    scraping_tasks[task_id]["processed_pages"] = 0
    scraping_tasks[task_id]["total_pages"] = 1  # Au moins l'URL de départ
    scraping_tasks[task_id]["progress"] = 0
    scraping_tasks[task_id]["url"] = start_url

    async with aiohttp.ClientSession() as session:
        while queue:
            # Traiter au maximum 10 URLs en parallèle
            batch_urls = []
            for _ in range(min(10, len(queue))):
                if not queue:
                    break
                url = queue.popleft()
                url = normalize_url(url)
                if url in visited:
                    continue
                visited.add(url)
                batch_urls.append(url)

            # Traiter ce lot d'URLs en parallèle
            tasks = [
                process_url(url, session, base_netloc, base_path, visited, url_to_markdown, total_urls, task_id)
                for url in batch_urls
            ]
            results = await asyncio.gather(*tasks)

            # Ajouter les nouvelles URLs découvertes à la queue
            for new_urls in results:
                for url in new_urls:
                    if url not in visited:
                        queue.append(url)

    # Combiner tout le contenu Markdown en un seul texte
    all_markdown = "\n\n".join(url_to_markdown.values())

    # Mettre à jour l'état de la tâche
    scraping_tasks[task_id]["status"] = "completed"
    scraping_tasks[task_id]["progress"] = 100
    scraping_tasks[task_id]["end_time"] = datetime.now().isoformat()
    scraping_tasks[task_id]["markdown_content"] = all_markdown
    scraping_tasks[task_id]["url_to_markdown"] = url_to_markdown

    return url_to_markdown


def start_scraping_task(url: str) -> str:
    """Démarre une tâche de scraping et retourne son identifiant."""
    task_id = str(uuid.uuid4())
    
    # Initialiser l'état de la tâche
    scraping_tasks[task_id] = {
        "status": "running",
        "url": url,
        "start_time": None,
        "end_time": None,
        "processed_pages": 0,
        "total_pages": 0,
        "progress": 0,
        "markdown_content": None,
        "url_to_markdown": None
    }
    
    # Lancer la tâche en arrière-plan
    asyncio.create_task(crawl_and_collect_async(url, task_id))
    
    return task_id


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


def get_url_to_markdown(task_id: str) -> Optional[Dict[str, str]]:
    """Récupère la cartographie URL -> Markdown d'une tâche de scraping terminée."""
    if task_id not in scraping_tasks or scraping_tasks[task_id]["status"] != "completed":
        return None
    
    return scraping_tasks[task_id].get("url_to_markdown")
