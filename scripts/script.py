""" Script pour extraire le contenu Markdown de la documentation d'un site web et le sauvegarder dans un fichier unique et une arborescence de fichiers. """
import os
from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

import html2text
import requests
from bs4 import BeautifulSoup


def normalize_url(url):
    """Normalise l'URL en supprimant le fragment et la barre oblique finale."""
    url, frag = urldefrag(url)
    if url.endswith("/"):
        url = url[:-1]
    return url


def get_file_path_from_url(url, base_url, output_dir):
    """Convertit une URL en chemin de fichier local pour l'arborescence."""
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

    # Assurez-vous que le chemin se termine par .md
    if not relative_path.endswith(".md"):
        if relative_path.endswith("/"):
            relative_path = relative_path[:-1]
        relative_path += ".md"

    return os.path.join(output_dir, relative_path)


def ensure_directory_exists(file_path):
    """Crée le répertoire pour un fichier donné s'il n'existe pas."""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def crawl_and_collect(start_url, file_name_output, tree_output_dir):
    """
    Parcourt la documentation à partir de l'URL de départ et collecte le contenu Markdown de chaque page.
    Écrit à la fois un fichier unique et une arborescence de fichiers.
    """
    visited = set()
    queue = deque()
    queue.append(start_url)
    base_netloc = urlparse(start_url).netloc
    base_path = urlparse(start_url).path

    # Dictionnaire pour stocker les contenus Markdown par URL
    url_to_markdown = {}

    while queue:
        url = queue.popleft()
        url = normalize_url(url)
        if url in visited:
            continue
        visited.add(url)
        print(f"Traitement de : {url}")

        try:
            response = requests.get(url)
            if response.status_code != 200:
                continue
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")

            # Extraire le contenu principal
            main_content = soup.find("main", {"id": "article-contents"})
            if main_content is None:
                # Si la structure est différente, utiliser le corps principal
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
            else:
                # Aucun titre de niveau 1 trouvé, ignorer cette page
                continue

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
                    queue.append(next_url)

        except Exception as e:
            print(f"Échec du traitement de {url}: {e}")

    # Écrire tout le contenu Markdown dans un seul fichier
    all_markdown = "\n\n".join(url_to_markdown.values())

    # Assurer que le répertoire pour le fichier unique existe
    ensure_directory_exists(file_name_output)
    with open(file_name_output, "w", encoding="utf-8") as f:
        f.write(all_markdown)

    print(f"Fichier unique créé avec succès: {file_name_output}")

    # Créer l'arborescence de fichiers
    if not os.path.exists(tree_output_dir):
        os.makedirs(tree_output_dir, exist_ok=True)

    for url, content in url_to_markdown.items():
        file_path = get_file_path_from_url(url, start_url, tree_output_dir)
        ensure_directory_exists(file_path)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fichier créé: {file_path}")


if __name__ == "__main__":
    # URL de départ (par exemple, la documentation GitHub Copilot)
    START_URL = "https://code.visualstudio.com/docs/copilot/chat/prompt-crafting"
    FILE_NAME_OUTPUT = "extract/vscode-prompt.md"
    TREE_OUTPUT_DIR = "extract/vscode_tree"
    # FILE_NAME_OUTPUT = "extract/githubactions.md"
    # TREE_OUTPUT_DIR = "extract/githubactions_tree"
    # START_URL = "https://docs.github.com/fr/copilot"
    # FILE_NAME_OUTPUT = "extract/documentation_github_copilot.md"
    # TREE_OUTPUT_DIR = "extract/copilot_tree"
    crawl_and_collect(START_URL, FILE_NAME_OUTPUT, TREE_OUTPUT_DIR)
