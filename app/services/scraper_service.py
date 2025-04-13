"""Service de scraping de documentation web vers markdown."""

import asyncio
import uuid
import zipfile
from collections import deque
from datetime import datetime
from io import BytesIO
from urllib.parse import urldefrag, urljoin, urlparse

import aiohttp
import html2text
from bs4 import BeautifulSoup

from app.schemas.scraper_schemas import ExportFormat

# Dictionnaire global pour suivre la progression des tâches de scraping
scraping_tasks: dict[str, dict] = {}


def normalize_url(url: str) -> str:
    """Normalise l'URL en supprimant le fragment et la barre oblique finale."""
    url, _ = urldefrag(url)
    if url.endswith("/"):
        url = url[:-1]
    return url


def get_file_path_from_url(url: str, base_url: str) -> str:
    """Convertit une URL en chemin de fichier relatif."""
    base_parsed = urlparse(base_url)
    url_parsed = urlparse(url)

    # Si l'URL ne contient qu'un chemin relatif
    if url_parsed.path.startswith(base_parsed.path):
        relative_path = url_parsed.path[len(base_parsed.path) :].lstrip("/")
    else:
        relative_path = url_parsed.path.lstrip("/")

    # S'il n'y a pas de chemin, utiliser 'index'
    if not relative_path:
        relative_path = "index"

    # Convertir les chemins en noms de fichiers valides
    # Remplacer les caractères non alphanumériques par des tirets
    import re

    relative_path = re.sub(r"[^a-zA-Z0-9/\-_]", "-", relative_path)

    # S'assurer qu'il n'y a pas de double tirets
    relative_path = re.sub(r"-+", "-", relative_path)

    # Assurez-vous que le chemin se termine par .md
    if not relative_path.endswith(".md"):
        if relative_path.endswith("/"):
            relative_path = relative_path[:-1]
        relative_path += ".md"

    return relative_path


async def process_url(
    url: str,
    session: aiohttp.ClientSession,
    base_netloc: str,
    base_path: str,
    visited: set[str],
    url_to_markdown: dict[str, str],
    total_urls: list[str],
    task_id: str,
) -> list[str]:
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

            # Stocker le contenu Markdown associé à l'URL - même si aucun titre h1 n'est trouvé
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
            100,
            int(
                (scraping_tasks[task_id]["processed_pages"] / max(len(total_urls), 1)) * 100
            ),
        )

    except Exception as e:
        logging.error(f"Échec du traitement de {url}: {e}")
    return new_urls_to_process


async def crawl_and_collect_async(start_url: str, task_id: str) -> dict[str, str]:
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
                process_url(
                    url,
                    session,
                    base_netloc,
                    base_path,
                    visited,
                    url_to_markdown,
                    total_urls,
                    task_id,
                )
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

    # Créer le contenu ZIP si nécessaire
    zip_content = None
    if scraping_tasks[task_id]["format"] in [ExportFormat.ZIP_FILES, ExportFormat.ZIP_FLAT]:
        try:
            # Créer un buffer en mémoire pour le ZIP
            zip_buffer = BytesIO()

            # Créer un fichier ZIP avec compression
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # Pour chaque URL, ajouter un fichier dans le ZIP
                for i, (url, markdown_content) in enumerate(url_to_markdown.items()):
                    # Déterminer le chemin du fichier en fonction du format
                    if scraping_tasks[task_id]["format"] == ExportFormat.ZIP_FILES:
                        # Format hiérarchique - conserver la structure des dossiers
                        file_path = get_file_path_from_url(url, start_url)
                    else:  # ZIP_FLAT
                        # Format plat - tous les fichiers à la racine
                        # Extraire uniquement le nom du fichier et ajouter un indice pour éviter les collisions
                        parsed_url = urlparse(url)
                        path_segments = parsed_url.path.strip("/").split("/")
                        file_name = path_segments[-1] if path_segments else f"page_{i}"
                        if not file_name:
                            file_name = f"page_{i}"
                        if not file_name.endswith(".md"):
                            file_name = f"{file_name}.md"
                        # Nettoyer le nom de fichier des caractères non valides
                        import re

                        file_name = re.sub(r"[^a-zA-Z0-9\-_.]", "-", file_name)
                        file_name = re.sub(r"-+", "-", file_name)
                        # Ajouter un index pour éviter les doublons
                        file_path = f"{i + 1:03d}_{file_name}"

                    # Éviter les doublons dans les noms de fichiers
                    if not file_path:
                        file_path = f"page_{i}.md"

                    # Encoder le contenu en bytes avec utf-8
                    encoded_content = markdown_content.encode("utf-8")

                    # Ajouter le fichier au ZIP
                    zip_file.writestr(file_path, encoded_content)

                # Ajouter un fichier README avec des informations sur le scraping
                readme_content = f"""# Documentation scrapée depuis {start_url}

Date: {datetime.now().isoformat()}
Nombre de pages: {len(url_to_markdown)}

## Pages incluses:

{chr(10).join([f"- [{url}]({url})" for url in url_to_markdown.keys()])}
"""
                zip_file.writestr("README.md", readme_content.encode("utf-8"))

            # Rembobiner le buffer et récupérer le contenu
            zip_buffer.seek(0)
            zip_content = zip_buffer.getvalue()

        except Exception as e:
            print(f"Erreur lors de la création du ZIP: {e}")
            # En cas d'erreur, on crée quand même un fichier ZIP de base avec un message d'erreur
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                error_message = f"Erreur lors de la création du ZIP: {e}\n\nContenu brut:\n\n{all_markdown}"
                zip_file.writestr("error.md", error_message.encode("utf-8"))
            zip_buffer.seek(0)
            zip_content = zip_buffer.getvalue()

    # Mettre à jour l'état de la tâche
    scraping_tasks[task_id]["status"] = "completed"
    scraping_tasks[task_id]["progress"] = 100
    scraping_tasks[task_id]["end_time"] = datetime.now().isoformat()
    scraping_tasks[task_id]["markdown_content"] = all_markdown
    scraping_tasks[task_id]["url_to_markdown"] = url_to_markdown
    scraping_tasks[task_id]["zip_content"] = zip_content

    return url_to_markdown


def start_scraping_task(
    url: str, format: ExportFormat = ExportFormat.SINGLE_FILE, filename: str | None = None
) -> str:
    """Démarre une tâche de scraping et retourne son identifiant."""
    task_id = str(uuid.uuid4())

    # Extraire le dernier segment de l'URL pour le nom du fichier si non fourni
    if not filename:
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.strip("/").split("/")
        filename = (
            path_segments[-1] if path_segments and path_segments[-1] else "documentation"
        )

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
        "url_to_markdown": None,
        "zip_content": None,
        "format": format,
        "filename": filename,
    }

    # Lancer la tâche en arrière-plan
    asyncio.create_task(crawl_and_collect_async(url, task_id))

    return task_id


def get_task_status(task_id: str) -> dict:
    """Récupère le statut d'une tâche de scraping."""
    if task_id not in scraping_tasks:
        return {"status": "not_found"}

    return scraping_tasks[task_id]


def get_markdown_content(task_id: str) -> str | None:
    """Récupère le contenu Markdown d'une tâche de scraping terminée."""
    if task_id not in scraping_tasks or scraping_tasks[task_id]["status"] != "completed":
        return None

    return scraping_tasks[task_id].get("markdown_content")


def get_zip_content(task_id: str) -> bytes | None:
    """Récupère le contenu ZIP d'une tâche de scraping terminée."""
    if task_id not in scraping_tasks or scraping_tasks[task_id]["status"] != "completed":
        return None

    return scraping_tasks[task_id].get("zip_content")


def get_url_to_markdown(task_id: str) -> dict[str, str] | None:
    """Récupère la cartographie URL -> Markdown d'une tâche de scraping terminée."""
    if task_id not in scraping_tasks or scraping_tasks[task_id]["status"] != "completed":
        return None

    return scraping_tasks[task_id].get("url_to_markdown")


def get_task_filename(task_id: str) -> str | None:
    """Récupère le nom de fichier d'une tâche de scraping."""
    if task_id not in scraping_tasks:
        return None

    return scraping_tasks[task_id].get("filename", "documentation")
