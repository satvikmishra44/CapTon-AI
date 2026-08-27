from textwrap import shorten
import logging
import re

from ddgs import DDGS

logger = logging.getLogger(__name__)


def _clean_query(text: str, max_words: int = 20) -> str:
    """Turn arbitrary script text into a short, search-friendly query."""
    text = re.sub(r"\s+", " ", text or "").strip()

    if not text:
        return ""

    # Remove obvious markup/punctuation noise while keeping useful search terms.
    text = re.sub(r"[<>]", " ", text)
    text = re.sub(r"[^\w\s.,!?%₹$€-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    words = text.split()
    return " ".join(words[:max_words])


def generate_query(script: str) -> str:
    """
    Generate a short, robust search query from the script.

    The old implementation sent the first 150 characters of the script
    directly to DDGS, which can produce poor/overly-specific queries.
    """
    cleaned = _clean_query(script, max_words=24)

    if not cleaned:
        return "social media video topic"

    return f"{cleaned} video topic"


def _search_ddgs(query: str, max_results: int) -> list[dict]:
    """Perform one DDGS search attempt."""
    with DDGS() as ddgs:
        return ddgs.text(
            query=query,
            max_results=max_results,
        )


def fetch_seo_data(script: str, max_results: int = 5) -> str:
    """
    Fetch SEO/search context without allowing search failure
    to kill the entire generation pipeline.

    DDGS may return no results because of temporary upstream
    failures, rate limits, backend changes, or an overly-specific
    query. In those cases we retry with progressively simpler
    queries and finally return a fallback context.
    """
    max_results = max(1, min(int(max_results), 10))

    cleaned = _clean_query(script, max_words=24)

    queries = [
        f"{cleaned} video topic" if cleaned else "",
        f"{_clean_query(script, max_words=12)}" if cleaned else "",
        "social media content trends",
    ]

    # Remove duplicates/empty queries while preserving order.
    queries = list(dict.fromkeys(q for q in queries if q))

    for attempt, query in enumerate(queries, start=1):
        logger.info(
            "Performing SEO search attempt %d/%d: %r",
            attempt,
            len(queries),
            query,
        )

        try:
            results = _search_ddgs(query, max_results)

            if not results:
                logger.warning(
                    "DDGS returned no results for query: %r",
                    query,
                )
                continue

            formatted = []

            for idx, result in enumerate(results, start=1):
                if not isinstance(result, dict):
                    continue

                title = str(result.get("title") or "").strip()
                snippet = str(result.get("body") or "").strip()
                href = str(result.get("href") or "").strip()

                if not title and not snippet:
                    continue

                short_snip = shorten(
                    snippet,
                    width=220,
                    placeholder="...",
                )

                if href:
                    formatted.append(
                        f"{idx}. {title} - {short_snip} ({href})"
                    )
                else:
                    formatted.append(
                        f"{idx}. {title} - {short_snip}"
                    )

            if formatted:
                seo_data = "\n".join(formatted)

                logger.info(
                    "SEO data fetched successfully: %d characters",
                    len(seo_data),
                )

                return seo_data

            logger.warning(
                "DDGS returned results, but none contained usable content."
            )

        except Exception as exc:
            # Search failure is non-fatal. Try the next query.
            logger.warning(
                "SEO search attempt %d failed: %s",
                attempt,
                exc,
            )

    # Final fallback.
    #
    # This is deliberately non-empty so the downstream AI agents can
    # continue working from the original script even when web search
    # is temporarily unavailable.
    fallback_topic = _clean_query(script, max_words=20)

    fallback = (
        "Live SEO search was unavailable for this request. "
        "Use the original script to infer the topic, audience, "
        "search intent, keywords, and relevant content angles."
    )

    if fallback_topic:
        fallback += f"\nLikely topic context: {fallback_topic}"

    logger.warning(
        "SEO search unavailable after %d attempts; using fallback context.",
        len(queries),
    )

    return fallback
