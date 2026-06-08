import os
import json
from crewai import Agent, Task, Crew, Process, LLM
from seo_tools import fetch_seo_data

key = os.getenv("GEMINI_API_KEY")
if not key:
    raise ValueError("Gemini Key Not Available Or Read By Agent")

llm = LLM("gemini/gemini-3.1-flash-lite", api_key=key)

def agents():
    # Analysis Agent
    analyzer = Agent(
        role = "Script Analyzer",
        goal=("Deeply analyze the given video script and extract topic, target audience, emotional tone, and main content angle."),
        backstory = ("You are a strategic content analyst who understands social media audiences. You break scripts into clear, structured insights that other agents can use."),
        llm = llm, 
        verbose = True
    )

    # Writing Agent (Extending Hook Capability)
    writer = Agent(
        role = "Hook, Hashtag And Caption Writer",
        goal=("Use a structured analysis plus the script and SEO web context to write viral-style hooks and a high-converting, extra informative and CTA Engagement Oriented multi-platform caption that works on Instagram, Facebook And YouTube."),
        backstory=("You are an expert social media copywriter who blends audience psychology, viral hook patterns, and SEO keywords to grow reach on YouTube, Instagram, and Facebook."),
        llm = llm,
        verbose = True
    )

    return analyzer, writer

def analysis_task(script: str, seo_data: str, analyzer: Agent) -> Task:
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
             "7. Hook Angle Ideas: (2-3 short notes on what kind of hooks might work "
            "best, e.g. problem, curiosity, bold claim, result, etc.)\n"
            "8. Hashtag Themes: (2-3 short notes on what themes or topics the hashtags "
            "should reflect, based on both the script and SEO context.)\n"
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

def writing_task(script: str, seo_data: str, analysis: Task, writer: Agent) -> Task:
    return Task(
        description=(
          "You are a social media hook + caption writer.\n"
            "You will receive, in your context:\n"
            "- A structured analysis of the script from another agent.\n"
            "- Web search results related to the topic (SEO context).\n"
            "You are also given the original script between <script> and </script>.\n\n"
            "Your job:\n"
            "1. Read and use the analysis and SEO context.\n"
            "2. Generate THREE short viral-style hooks (for YouTube Shorts, Instagram Reels, and Facebook Reels).\n"
            "   - Each hook must be 5-12 words and in devnagri hindi.\n"
            "   - Use proven patterns like: problem hook, curiosity hook, bold claim hook, or result hook.\n"
            "   - Hooks must stand alone as the opening line of a video or caption.\n"
            "3. Generate ONE main caption (1-3 short sentences) that:\n"
            "   - Is optimized for YouTube, Instagram, and Facebook.\n"
            "   - Tell The Actual Reality Of Things Told In The Video Along With More Info On That Topic(But In The Similar Language Of Script)\n"
            "   - Naturally weaves in as much SEO-relevant phrases as much as possible that match real search intent.\n"
            "   - Still sounds human and not keyword-stuffed.\n"
            "4. Generate EXACTLY FOUR relevant, platform-agnostic hashtags that:\n"
            "   - Reflect the main topic and audience.\n"
            "   - Are short and readable (no extremely long hashtag strings).\n"
            "   - Avoid ultra-generic tags like #fyp, #viral, #trending, #shorts.\n"
            "   - Are safe to use across YouTube, Instagram, and Facebook.\n"
            "5. Do NOT paste the full script or full SEO results.\n"
            "6. Output MUST follow this exact format (no extra text):\n"
            "Hooks:\n"
            "1) <first hook>\n"
            "2) <second hook>\n"
            "3) <third hook>\n"
            "\n"
            "Caption:\n"
            "<final caption text here>\n\n"
            f"<script>\n{script}\n</script>\n\n"
            f"<seo>\n{seo_data}\n</seo>"
        ),
        expected_output=(
            "Generate THREE short viral-style hooks ..."
            "   - Each hook must be 5-12 words."
            "   - Use proven patterns like: problem hook, curiosity hook, bold claim hook, or result hook."
            " Generate ONE main caption (4-7 short sentences) that:"
            "   - Is optimized for YouTube, Instagram, and Facebook."
            "   - Naturally weaves in as much SEO-relevant phrases in a human sounding way"
            "Output MUST follow this exact format (no extra text):\n"
            "Hooks:\n"
            "1) <first hook>\n"
            "2) <second hook>\n"
            "3) <third hook>\n"
            "\n"
            "Caption:\n"
            "<final caption text here>\n \n"
            "Hashtags:\n"
            "#tag1 #tag2 #tag3 #tag4\n\n"
            "MOST IMPORTANT: Return your final answer as VALID JSON ONLY, with this exact schema:\n"
            "{\n"
            '  "hooks": ["hook1", "hook2", "hook3"],\n'
            '  "caption": "caption text here",\n'
            '  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4"]\n'
            "}\n"
            "Rules for JSON output:\n"
            "- Do NOT include any explanation, prose, markdown, or backticks.\n"
            "- Do NOT wrap the JSON in ```json or any other fences.\n"
            "- Use double quotes for all keys and string values (valid JSON).\n"
            "- The value for 'hooks' must be a list of exactly 3 strings.\n"
            "- The value for 'hashtags' must be a list of exactly 4 strings.\n"
            "- Start your response with '{' and end it with '}'.\n"
        ),
        agent = writer,
        # Context Tells The Agent The Current Point Of Discussion So That He Could Have A Better Understanding Of What's Going On And What's Needed From Him
        context=[analysis]
    )

def parsing_output(output: str):
    try: 
        return json.loads(str(output))
    except json.JSONDecodeError as e:
        print("!! Failed to parse JSON output from writer agent.")
        print("Error:", e)
        print("Raw output was:\n", output)
        return None
    
def run(script: str):
    print("Starting SEO + multi-agent CrewAI workflow... \n")

    seo_context = fetch_seo_data(script)
    print(f"SEO Context Ready: {seo_context} \n")

    analyzer, writer = agents()
    print("[✓] Analyzer and JSON Writer agents ready \n")

    analysis = analysis_task(script, seo_context, analyzer)
    writing = writing_task(script, seo_context, analysis, writer)

    crew = Crew(agents=[analyzer, writer], tasks=[analysis, writing], process=Process.sequential)

    print("Running AI Agent Crew... \n")
    data = crew.kickoff()

    print("\n JSON String Recieved \n")

    result = parsing_output(data)

    if result is None:
        print("No Valid JSON to display \n")
        return None

    print("JSON Parsed Succesfully \n")
    return result 
