"""Schémas pour l'API de scraping."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class ScraperRequest(BaseModel):
    """Schéma pour la requête de scraping."""

    url: HttpUrl

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        """Vérifie que l'URL est valide."""
        if not v:
            raise ValueError("L'URL ne peut pas être vide")
        return v


class ScraperResponse(BaseModel):
    """Schéma pour la réponse de création d'une tâche de scraping."""

    task_id: str
    status: str
    message: str
    model_config = ConfigDict(from_attributes=True)


class TaskStatus(BaseModel):
    """Schéma pour le statut d'une tâche de scraping."""

    task_id: str
    status: str
    url: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    progress: int = 0
    processed_pages: int = 0
    total_pages: int = 0
    model_config = ConfigDict(from_attributes=True)


class ContentResponse(BaseModel):
    """Schéma pour la réponse de contenu d'une tâche de scraping."""

    task_id: str
    url: str
    content: str
    status: str = "success"
    timestamp: str
    model_config = ConfigDict(from_attributes=True)
