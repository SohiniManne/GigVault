import httpx
from app.config import get_settings

settings = get_settings()


async def get_news_disruption_signal(city=None):
    try:
        query = f"{city} traffic OR rain OR flood OR disruption"

        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={query}&language=en&sortBy=publishedAt&apiKey={settings.news_api_key}"
        )

        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            data = res.json()

        articles = data.get("articles", [])[:3]

        if not articles:
            return {
                "disruption_detected": False,
                "headlines": [],
                "source": "newsapi"
            }

        headlines = [a["title"] for a in articles]

        return {
            "disruption_detected": True,
            "headlines": headlines,
            "source": "newsapi"
        }

    except Exception as e:
        print("News API failed:", e)
        return {
            "disruption_detected": False,
            "headlines": [],
            "source": "fallback"
        }
