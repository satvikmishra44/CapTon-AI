"""
Central place for turning raw/technical exceptions (LiteLLM/Gemini errors,
network errors, JSON parsing errors, etc.) into short, human-readable
messages that are safe to show directly in the UI.

Usage:
    from error_utils import extract_friendly_error
    try:
        ...
    except Exception as e:
        logging.exception("Step X failed")          # full traceback -> server logs
        raise RuntimeError(extract_friendly_error(e)) from e   # clean msg -> user
"""

import re
import json


# Known HTTP / provider status codes -> friendly text.
_STATUS_MAP = {
    "503": "This model is currently experiencing high demand. Please try again in a moment.",
    "429": "Too many requests right now (rate limit reached). Please wait a few seconds and try again.",
    "500": "The AI provider hit an internal error. Please try again shortly.",
    "504": "The request to the AI provider timed out. Please try again.",
    "401": "Authentication with the AI provider failed. Please check the API key.",
    "403": "Access to the AI model was denied. Please check API key permissions or billing.",
}

# Known local/internal error phrases -> friendly text. Checked case-insensitively.
_PHRASE_MAP = {
    "gemini key not available": "The Gemini API key is missing or not configured on the server.",
    "seo context could not be fetched": "We couldn't fetch live SEO data right now. Please try again.",
    "failed to parse json output": "The AI returned an unexpected response format. Please try again.",
    "writer returned empty outputs": "The AI didn't return any usable content. Please try again.",
    "analysis completed but returned empty text": "The analysis step returned no content. Please try again.",
    "connectionerror": "Couldn't connect to the AI/search service. Check your internet connection and try again.",
    "connection aborted": "The connection to the AI/search service was interrupted. Please try again.",
    "timeout": "The request timed out. Please try again.",
    "ratelimiterror": "Too many requests right now (rate limit reached). Please wait a few seconds and try again.",
    "no script provided": "Please paste a script before generating.",
    "ddgs": "The web search service used for SEO context is temporarily unavailable.",
}


def extract_friendly_error(error) -> str:
    """Return a short, user-safe message for any exception/string raised anywhere
    in the pipeline (LLM errors, network errors, parsing errors, custom errors)."""
    text = str(error).strip()
    if not text:
        return "An unknown error occurred. Please try again."

    # 1) Try to pull a JSON object out of the text and read its "message" field.
    #    Covers LiteLLM/Gemini style errors, e.g.:
    #    503 UNAVAILABLE. {'error': {'code': 503, 'message': '...', 'status': 'UNAVAILABLE'}}
    brace_idx = text.find("{")
    if brace_idx != -1:
        blob = text[brace_idx:]
        for candidate in (blob, blob.replace("'", '"')):
            try:
                data = json.loads(candidate)
                err_obj = data.get("error", data) if isinstance(data, dict) else None
                if isinstance(err_obj, dict) and err_obj.get("message"):
                    return str(err_obj["message"]).strip()
            except Exception:
                pass

    # 2) Regex fallback in case the JSON blob doesn't fully parse.
    match = re.search(r"""['"]message['"]\s*:\s*['"](.+?)['"]\s*[,}]""", text)
    if match:
        return match.group(1).strip()

    # 3) Known status codes.
    for code, msg in _STATUS_MAP.items():
        if re.search(rf"\b{code}\b", text):
            return msg

    # 4) Known local phrases.
    lowered = text.lower()
    for phrase, msg in _PHRASE_MAP.items():
        if phrase in lowered:
            return msg

    # 5) Fallback: trimmed raw text (still better than a stack trace).
    return text[:300]