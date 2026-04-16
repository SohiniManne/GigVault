from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.config import get_settings

KEYWORDS = ["strike", "bandh", "curfew", "road blocked"]


async def get_news_disruption_signal(*, city: Optional[str]) -> Dict[str, Any]:
    settings = get_settings()
    query = f"{city or 'india'} strike OR bandh OR curfew OR 'road blocked'"
    if not settings.news_api_key.strip():
        return {"disruption_detected": False, "keywords_found": [], "source": "news_mock"}

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 20,
                    "apiKey": settings.news_api_key.strip(),
                },
            )
            resp.raise_for_status()
            data = resp.json()
        articles = data.get("articles") or []
        text_blob = " ".join(
            f"{a.get('title','')} {a.get('description','')}".lower() for a in articles
        )
        found = [k for k in KEYWORDS if k in text_blob]
        return {"disruption_detected": len(found) > 0, "keywords_found": found, "source": "newsapi"}
    except Exception:
        return {"disruption_detected": False, "keywords_found": [], "source": "newsapi_error"}
