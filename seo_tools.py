import logging
from textwrap import shorten
from ddgs import DDGS

logger = logging.getLogger(__name__)


def generate_query(script: str) -> str:
    # Intro Of Script To Get The Main Topic
    cleaned = " ".join(script.split())
    intro = shorten(cleaned, width=150, placeholder="...")
    return f"{intro} YouTube Video Topic"


def fetch_seo_data(script: str, max_results: int = 5) -> str:
    """Fetches lightweight SEO context via DuckDuckGo search.

    Raises on real failures (network/search errors) so the caller can decide
    whether that's fatal. Returns "" (no exception) when the search succeeds
    but simply finds nothing — that's a normal, non-fatal outcome.
    """
    query = generate_query(script)
    logger.info("Performing SEO search for %r", query)

    result = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            for idx, r in enumerate(results, start=1):
                title = r.get("title") or ""
                snippet = r.get("body") or ""
                href = r.get("href") or ""

                if not title and not snippet:
                    continue

                # Shortening For Manageable Context
                short_snip = shorten(snippet, width=180, placeholder="...")
                result.append(f"{idx}. {title} - {short_snip} ({href})")

    except Exception as e:
        logger.exception("SEO search failed")
        raise RuntimeError(f"SEO search failed: {e}") from e

    if not result:
        logger.warning("SEO search returned no results for query: %r", query)

    seo_data = "\n".join(result)
    logger.info("SEO data fetched (%d results)", len(result))
    return seo_data