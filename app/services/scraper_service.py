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


def get_file_path_from_url(url: str, base_url: str, output_dir: str) -> str:
    """Convertit une URL en chemin de fichier local pour l'arborescence."""
    base_parsed = urlparse(base_url)
    url_parsed = urlparse(url)

    # Si l'URL ne contient qu'un chemin relatif
    if url_parsed.path.startswith(base_parsed.path):
        relative_path = url_parsed.path[len(base_parsed.path):].lstrip("/")
    else:
        relative_path = url_parsed.path.lstrip("/")

    # S'il n'y a pas de chemin, utiliser 'index'
    if not relative_path:
        relative_path = "index"

    # Assurez-vous que le chemin se termine par .md
    if not relative_path.endswith(".md"):
        if relative_path.endswith("/"):
            relative_path = relative_path[:-1]
        relative_path += ".md"

    return os.path.join(output_dir, relative_path)


def ensure_directory_exists(file_path: str) -> None:
    """Crée le répertoire pour un fichier donné s'il n'existe pas."""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


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


async def crawl_and_collect_async(start_url: str, output_dir: Optional[str] = None, task_id: str = None) -> Tuple[str, Dict[str, str], str]:
    """
    Version asynchrone de la fonction de crawl qui parcourt la documentation
    et collecte le contenu Markdown de chaque page.
    
    Si output_dir est None, ne sauvegarde pas sur disque et retourne uniquement le contenu.
    """
    # Configuration des chemins de sortie si demandé
    single_file_path = None
    tree_dir = None
    
    if output_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        single_file_dir = os.path.join(output_dir, "single")
        tree_dir = os.path.join(output_dir, "tree", timestamp)
        
        # Assurer que les répertoires existent
        ensure_directory_exists(single_file_dir)
        ensure_directory_exists(tree_dir)
        
        single_file_path = os.path.join(single_file_dir, f"{task_id}.md")
    
    # Initialisation des structures de données
    visited = set()
    queue = deque([start_url])
    total_urls = [start_url]
    base_netloc = urlparse(start_url).netloc
    base_path = urlparse(start_url).path
    url_to_markdown = {}

    # Initialiser la progression si task_id est fourni
    if task_id:
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
    
    # Sauvegarder sur disque si un répertoire de sortie est spécifié
    if output_dir:
        # Écrire dans un fichier unique
        with open(single_file_path, "w", encoding="utf-8") as f:
            f.write(all_markdown)

        # Créer l'arborescence de fichiers
        for url, content in url_to_markdown.items():
            file_path = get_file_path_from_url(url, start_url, tree_dir)
            ensure_directory_exists(file_path)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    # Mettre à jour l'état de la tâche si task_id est fourni
    if task_id:
        scraping_tasks[task_id]["status"] = "completed"
        scraping_tasks[task_id]["progress"] = 100
        scraping_tasks[task_id]["end_time"] = datetime.now().isoformat()
        if output_dir:
            scraping_tasks[task_id]["output_file"] = single_file_path
            scraping_tasks[task_id]["output_dir"] = tree_dir
        scraping_tasks[task_id]["markdown_content"] = all_markdown

    return single_file_path, url_to_markdown, all_markdown


def start_scraping_task(url: str, save_to_disk: bool = True) -> str:
    """Démarre une tâche de scraping et retourne son identifiant."""
    task_id = str(uuid.uuid4())
    
    # Créer le répertoire de sortie pour ce user/session si on sauvegarde sur disque
    output_dir = os.path.join("output", task_id) if save_to_disk else None
    
    # Initialiser l'état de la tâche
    scraping_tasks[task_id] = {
        "status": "running",
        "url": url,
        "start_time": None,
        "end_time": None,
        "processed_pages": 0,
        "total_pages": 0,
        "progress": 0,
        "output_file": None,
        "output_dir": output_dir,
        "markdown_content": None,
        "save_to_disk": save_to_disk
    }
    
    # Lancer la tâche en arrière-plan
    asyncio.create_task(crawl_and_collect_async(url, output_dir, task_id))
    
    return task_id


def get_task_status(task_id: str) -> Dict:
    """Récupère le statut d'une tâche de scraping."""
    if task_id not in scraping_tasks:
        return {"status": "not_found"}
    
    return scraping_tasks[task_id]


def get_result_content(task_id: str) -> Tuple[str, Optional[str]]:
    """Récupère le contenu du résultat d'une tâche de scraping."""
    if task_id not in scraping_tasks or scraping_tasks[task_id]["status"] != "completed":
        return None, None
    
    # Récupérer directement le contenu markdown si disponible
    content = scraping_tasks[task_id].get("markdown_content")
    if content:
        return content, None
    
    # Sinon essayer de lire le fichier
    file_path = scraping_tasks[task_id].get("output_file")
    if not file_path or not os.path.exists(file_path):
        return None, None
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content, file_path
