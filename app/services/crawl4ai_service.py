"""Service utilisant l'API crawl4ai pour extraire le contenu d'un site web."""
import json
import os
from datetime import datetime
from typing import Dict, Optional

import aiohttp

from app.services.task_store import scraping_tasks


async def fetch_mcp_crawl4ai(url: str, task_id: str) -> Dict:
    """
    Utilise l'API crawl4ai via Model Context Protocol pour extraire le contenu d'un site web.
    """
    # Mise à jour du statut initial
    scraping_tasks[task_id]["status"] = "running"
    scraping_tasks[task_id]["progress"] = 10
    scraping_tasks[task_id]["processed_pages"] = 0
    scraping_tasks[task_id]["total_pages"] = 1

    try:
        # Construire la requête MCP pour crawl4ai
        mcp_request = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that uses crawl4ai to extract documentation content."
                },
                {
                    "role": "user",
                    "content": f"Please crawl this URL and extract all documentation content in Markdown format: {url}"
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "crawl",
                        "description": "Crawl a website and extract content",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "The URL to crawl"
                                },
                                "max_pages": {
                                    "type": "number",
                                    "description": "Maximum number of pages to crawl"
                                }
                            },
                            "required": ["url"]
                        }
                    }
                }
            ],
            "tool_choice": {
                "type": "function",
                "function": {
                    "name": "crawl"
                }
            }
        }

        # URL de l'API crawl4ai (à remplacer par l'URL réelle)
        crawl4ai_api_url = os.environ.get("CRAWL4AI_API_URL", "https://api.crawl4ai.com/v1")

        # Mise à jour du statut
        scraping_tasks[task_id]["progress"] = 20
        
        # Appeler l'API MCP de crawl4ai
        async with aiohttp.ClientSession() as session:
            # Première requête pour initialiser le crawling
            async with session.post(
                f"{crawl4ai_api_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.environ.get('CRAWL4AI_API_KEY')}"
                },
                json=mcp_request
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Erreur lors de l'appel à crawl4ai: {error_text}")
                
                result = await response.json()
                
                # Mise à jour du statut
                scraping_tasks[task_id]["progress"] = 50
                scraping_tasks[task_id]["processed_pages"] = 1
        
            # Extraire le tool_call_id pour récupérer le résultat
            tool_call = result.get("choices", [{}])[0].get("message", {}).get("tool_calls", [{}])[0]
            tool_call_id = tool_call.get("id")
            
            # Si le tool_call_id n'est pas disponible, traiter l'erreur
            if not tool_call_id:
                raise Exception("Impossible d'obtenir l'ID d'appel d'outil depuis crawl4ai")
            
            # Attendre et récupérer le résultat du crawling
            async with session.post(
                f"{crawl4ai_api_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.environ.get('CRAWL4AI_API_KEY')}"
                },
                json={
                    "messages": mcp_request["messages"] + [
                        {
                            "role": "assistant", 
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": tool_call_id,
                                    "type": "function",
                                    "function": {
                                        "name": "crawl",
                                        "arguments": json.dumps({
                                            "url": url,
                                            "max_pages": 50
                                        })
                                    }
                                }
                            ]
                        },
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": "Crawling completed successfully. Processing content..."
                        }
                    ]
                }
            ) as tool_response:
                if tool_response.status != 200:
                    error_text = await tool_response.text()
                    raise Exception(f"Erreur lors de la récupération des résultats de crawl4ai: {error_text}")
                
                crawl_result = await tool_response.json()
                
                # Extraire le contenu markdown
                content = crawl_result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not content:
                    raise Exception("Aucun contenu n'a été extrait par crawl4ai")
                
                # Mise à jour du statut final
                scraping_tasks[task_id]["status"] = "completed"
                scraping_tasks[task_id]["progress"] = 100
                scraping_tasks[task_id]["end_time"] = datetime.now().isoformat()
                scraping_tasks[task_id]["markdown_content"] = content
                
                return {"success": True, "content": content}

    except Exception as e:
        # En cas d'erreur, mettre à jour le statut de la tâche
        scraping_tasks[task_id]["status"] = "error"
        scraping_tasks[task_id]["error"] = str(e)
        return {"success": False, "error": str(e)}


async def get_crawl4ai_content(task_id: str) -> Optional[str]:
    """Récupère le contenu extrait par crawl4ai pour une tâche donnée."""
    if task_id not in scraping_tasks:
        return None
    
    return scraping_tasks[task_id].get("markdown_content")