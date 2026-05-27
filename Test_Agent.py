import os
from textwrap import shorten
from crewai import Agent, Task, Crew, Process, LLM
from ddgs import DDGS

key = os.getenv("GEMINI_API_KEY")
if not key:
    raise ValueError("Gemini Key Not Available Or Read By Agent")

llm = LLM("gemini/gemini-3.1-flash-lite", api_key=key)

# Taking Script
def get_script():
    print("Enter Your Script: (Press Ctrl + Z + Enter To Finish)")
    print("-" * 60)
    try:
        lines = []
        while True:
            line = input()
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass

    script = "\n".join(lines).strip()

    if not script:
        raise ValueError("No Script Provided.")
    
    return script

# SEO Web Search
def generate_query(script: str) -> str:
    # Intro Of Script To Get The Main Topic
    cleaned = " ".join(script.split())
    intro = shorten(cleaned, width=150, placeholder="...")
    return f"{intro} YouTube Video Topic"

# Searching For SEO Keywords
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

# Defining Agents

# Analysis Agent
analyzer = Agent(
    role = "Script Analyzer",
    goal=("Deeply analyze the given video script and extract topic, target audience, emotional tone, and main content angle."),
    backstory = ("You are a strategic content analyst who understands social media audiences. You break scripts into clear, structured insights that other agents can use."),
    llm = llm, 
    verbose = True
)

# Writing Agent
writer = Agent(
    role = "Caption Writer",
    goal=("Use a structured analysis plus the script and SEO web context to write a high-converting, extra informative and CTA Engagement Oriented multi-platform caption that works on Instagram, Facebook And YouTube."),
    backstory=("You are an expert social media copywriter who uses clear insights from analysts to write sharp, scroll-stopping and engagement farming captions for YouTube, Instagram, and Facebook."),
    llm = llm,
    verbose = True
)

# Defining Task For Agent

def analyzing(script: str, seo_data: str) -> Task:
    return Task(
        description=(
             "You are given:\n"
            "A) A social media video script between <script> and </script>.\n"
            "B) Web search results about likely related topics between <seo> and </seo>.\n\n"
            "Use BOTH to produce a structured analysis with these sections:\n"
            "1. Main Topic: (one line)\n"
            "2. Target Audience: (one line)\n"
            "3. Emotional Tone: (one or two words)\n"
            "4. Content Angle / Promise: (one or two lines)\n"
            "5. Key Points or Benefits: (bullet-style list in plain text)\n"
            "6. SEO Keyword Ideas: (comma-separated list of short keyword phrases "
            "based on BOTH the script and web search results.)\n"
            "Do NOT write a caption here. Only return the analysis.\n\n"
            f"<script>\n{script}\n</script>\n\n"
            f"<seo>\n{seo_data}\n</seo>"
        ),
        agent = analyzer,
        expected_output=("A comprehensive analysis report following this exact format:\n"
            "1. Main Topic: [Single line description]\n"
            "2. Target Audience: [Single line description]\n"
            "3. Emotional Tone: [One or two words]\n"
            "4. Content Angle / Promise: [One or two sentences]\n"
            "5. Key Points or Benefits:\n"
            "- [Point 1]\n"
            "- [Point 2]\n"
            "- [Point 3]\n"
            "6. SEO Keyword Ideas: [Keyword1, Keyword2, Keyword3, Keyword4]\n"
        ))

def writing(script: str, seo_data: str, analysis: Task) -> Task:
    return Task(
        description=(
           "You are a social media caption writer.\n"
            "You will receive, in your context:\n"
            "- A structured analysis of the script from another agent.\n"
            "- Web search results related to the topic (SEO context).\n"
            "You are also given the original script between <script> and </script>.\n\n"
            "Your job:\n"
            "1. Read and use the analysis and SEO context.\n"
            "2. Write ONE caption (1-3 short sentences) that:\n"
            "   - Is optimized for YouTube, Instagram Reels, and Facebook.\n"
            "   - Hooks the viewer quickly.\n"
            "   - Naturally weaves in 2-4 SEO-relevant phrases that match real search intent.\n"
            "   - Still sounds human and not keyword-stuffed.\n"
            "3. Do NOT include hashtags or emojis.\n"
            "4. Do NOT repeat the full analysis text.\n"
            "5. Do NOT paste the full script.\n"
            "Return only the final caption.\n\n"
            f"<script>\n{script}\n</script>\n\n"
            f"<seo>\n{seo_data}\n</seo>"
        ),
        expected_output=(
            "A concise, high-converting social media caption (1-3 sentences) "
            "that incorporates SEO phrases naturally without emojis or hashtags. "
            "The output should contain ONLY the caption text."
        ),
        agent = writer,
        # Context Tells The Agent The Current Point Of Discussion So That He Could Have A Better Understanding Of What's Going On And What's Needed From Him
        context=[analysis]
    )

# Making All Agents A Crew And Running

def run():
    print("Starting Agent Crew...")
    script = get_script()
    print("Script Recieved...\n")
    print(f"Agent Started For Script... {script[:30]} \n")

    seo_data = fetch_seo_data(script=script)
    print(f"SEO Data Fetched... {seo_data}")

    print("Starting Analysis...")
    analysis = analyzing(script, seo_data=seo_data)

    print("Started Writing Caption...")
    caption = writing(script=script, analysis=analysis, seo_data=seo_data)

    crew = Crew(agents=[analyzer, writer], tasks=[analysis, caption], process=Process.sequential) # Runs Task In A One After Another Sequence

    print("Generating Captions...\n")
    result = crew.kickoff()
    print("Analysis completed")
    print("Caption Generated: \n")
    print(result)

run()