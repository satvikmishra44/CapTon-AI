from textwrap import shorten
from ddgs import DDGS
import traceback

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
            print(f"Got {len(results)} results from DDGS")  # Debug: log result count
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
        traceback.print_exc()  # Log full traceback
    
    if not result:
        print("⚠️ Warning: No SEO data found after search attempt.")

    seo_data = "\n".join(result)
    print(f"SEO Data Fetched: {len(seo_data)} characters")
    return seo_data
