import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Créer les répertoires de sortie s'ils n'existent pas
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/single", exist_ok=True)
    os.makedirs("output/tree", exist_ok=True)

    yield
    # Cleanup on shutdown


app = FastAPI(
    title="Documentation Scraper API",
    description="API pour extraire le contenu de la documentation d'un site web et le convertir en Markdown",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
