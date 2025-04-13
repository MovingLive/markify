"""Schémas pour l'API de scraping."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class ExportFormat(str, Enum):
    """Format d'exportation des données scrapées."""

    SINGLE_FILE = "single_file"
    ZIP_FILES = "zip_files"
    ZIP_FLAT = "zip_flat"


class ScraperRequest(BaseModel):
    """Schéma pour la requête de scraping."""

    url: HttpUrl
    format: ExportFormat = ExportFormat.SINGLE_FILE
    filename: str | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        """Vérifie que l'URL est valide."""
        if not v:
            raise ValueError("L'URL ne peut pas être vide")
        return v

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v):
        """Vérifie que le nom de fichier est valide."""
        if v and not v.strip():
            return None
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
    format: ExportFormat = ExportFormat.SINGLE_FILE
    filename: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ContentResponse(BaseModel):
    """Schéma pour la réponse de contenu d'une tâche de scraping."""

    task_id: str
    url: str
    content: str
    status: str = "success"
    timestamp: str
    format: ExportFormat = ExportFormat.SINGLE_FILE
    filename: str | None = None
    model_config = ConfigDict(from_attributes=True)
