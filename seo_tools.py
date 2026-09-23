# seo_tools.py — simple, free, no API keys
import time
import logging
from textwrap import shorten
from ddgs import DDGS
from ddgs.exceptions import DDGSException

logger = logging.getLogger(__name__)


def generate_query(script: str) -> str:
    cleaned = " ".join(script.split())
    intro = shorten(cleaned, width=150, placeholder="...")
    return f"{intro} YouTube Video Topic"


def _search_once(query: str, max_results: int) -> list:
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
        out = []
        for idx, r in enumerate(results, start=1):
            title = r.get("title") or ""
            snippet = r.get("body") or ""
            href = r.get("href") or ""
            if not title and not snippet:
                continue
            short_snip = shorten(snippet, width=180, placeholder="...")
            out.append(f"{idx}. {title} - {short_snip} ({href})")
        return out


def fetch_seo_data(script: str, max_results: int = 5) -> str:
    query = generate_query(script)
    logger.info("Performing SEO search for %r", query)

    result = []
    for attempt in (1, 2):  # one retry, all engines are free/scraped so no cost either way
        try:
            result = _search_once(query, max_results)
            break
        except DDGSException:
            if attempt == 2:
                logger.warning("No SEO results found for %r after retry — continuing without it.", query)
            else:
                time.sleep(1.5)
        except Exception as e:
            logger.warning("SEO search error (%s) — continuing without it.", e)
            break

    seo_data = "\n".join(result)
    logger.info("SEO data fetched (%d results)", len(result))
    return seo_data