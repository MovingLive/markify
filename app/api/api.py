from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, Path
from fastapi.responses import Response

from app.schemas.scraper_schemas import (
    ContentResponse,
    ScraperRequest,
    ScraperResponse,
    TaskStatus,
)
from app.services.scraper_service import (
    get_markdown_content,
    get_task_status,
    start_scraping_task,
)

api_router = APIRouter()


# health endpoint
@api_router.get("/health")
async def health():
    """Point de terminaison de vérification de l'état de l'API."""
    return {"status": "ok"}


@api_router.post("/scrape", response_model=ScraperResponse)
async def scrape_documentation(
    request: ScraperRequest, background_tasks: BackgroundTasks
) -> ScraperResponse:
    """
    Démarre une tâche de scraping pour l'URL spécifiée.

    La tâche s'exécute en arrière-plan et renvoie un identifiant de tâche unique
    que vous pouvez utiliser pour vérifier son état.
    """
    # Démarrer le scraping en arrière-plan
    task_id = start_scraping_task(str(request.url))

    return ScraperResponse(
        task_id=task_id,
        status="started",
        message="La tâche de scraping a été démarrée avec succès.",
    )


@api_router.get("/progress/{task_id}", response_model=TaskStatus)
async def get_scraping_progress(
    task_id: str = Path(..., description="L'identifiant de la tâche de scraping"),
) -> TaskStatus:
    """
    Récupère la progression d'une tâche de scraping spécifique.
    """
    task_status = get_task_status(task_id)

    if task_status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    return TaskStatus(
        task_id=task_id,
        status=task_status["status"],
        url=task_status.get("url"),
        start_time=task_status.get("start_time"),
        end_time=task_status.get("end_time"),
        progress=task_status.get("progress", 0),
        processed_pages=task_status.get("processed_pages", 0),
        total_pages=task_status.get("total_pages", 0),
    )


@api_router.get("/result/{task_id}", response_model=ContentResponse)
async def get_scraping_result(
    task_id: str = Path(..., description="L'identifiant de la tâche de scraping"),
) -> ContentResponse:
    """
    Récupère le résultat d'une tâche de scraping spécifique une fois qu'elle est terminée.
    """
    task_status = get_task_status(task_id)

    if task_status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    if task_status["status"] != "completed":
        raise HTTPException(status_code=400, detail="La tâche n'est pas encore terminée")

    content = get_markdown_content(task_id)

    if not content:
        raise HTTPException(status_code=404, detail="Contenu non trouvé")

    return ContentResponse(
        task_id=task_id,
        url=task_status.get("url", ""),
        content=content,
        status="success",
        timestamp=datetime.now().isoformat(),
    )


@api_router.get("/download/{task_id}")
async def download_markdown_file(
    task_id: str = Path(..., description="L'identifiant de la tâche de scraping"),
) -> Response:
    """
    Télécharge le fichier Markdown généré par une tâche de scraping spécifique.
    """
    task_status = get_task_status(task_id)

    if task_status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    if task_status["status"] != "completed":
        raise HTTPException(status_code=400, detail="La tâche n'est pas encore terminée")

    content = get_markdown_content(task_id)

    if not content:
        raise HTTPException(status_code=404, detail="Contenu non trouvé")

    # Extraire le nom du domaine de l'URL pour nommer le fichier
    url = task_status.get("url", "")
    filename = url.split("//")[-1].split("/")[0].replace(".", "_")
    filename = f"{filename}_{datetime.now().strftime('%Y%m%d')}.md"

    # Création d'une réponse directe à partir du contenu en mémoire
    response = Response(content=content, media_type="text/markdown")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
