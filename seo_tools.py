from textwrap import shorten
from ddgs import DDGS

def generate_query(script: str) -> str:
    # Intro Of Script To Get The Main Topic
    cleaned = " ".join(script.split())
    intro = shorten(cleaned, width=150, placeholder="...")
    return f"{intro} YouTube Video Topic"

def fetch_seo_data(script: str, max = 5) -> str:
    query = generate_query(script)
    print(f"Performing SEO Search for {query !r}")

    result = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max)
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
        print(f"Error In SEO Search: {e}")
    
    if not result:
        print("No SEO data found.")

    seo_data = "\n".join(result)
    print("SEO Data Fetched")
    return seo_data