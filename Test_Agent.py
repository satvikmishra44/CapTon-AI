import os
from crewai import Agent, Task, Crew, Process, LLM

key = os.getenv("GEMINI_API_KEY")
if not key:
    raise ValueError("Gemini Key Not Available Or Read By Agent")

llm = LLM("gemini/gemma-4-31b-it", api_key=key)

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
    goal=("Use a structured analysis plus the script to write a high-converting, extra informative and CTA Engagement Oriented multi-platform caption that works on Instagram, Facebook And YouTube."),
    backstory=("You are an expert social media copywriter who uses clear insights from analysts to write sharp, scroll-stopping and engagement farming captions for YouTube, Instagram, and Facebook."),
    llm = llm,
    verbose = True
)

# Defining Task For Agent

def analyzing(script: str) -> Task:
    return Task(
        description=(
             "You are given a social media video script between <script> and </script>.\n"
            "Analyze it and output a structured analysis with these sections:\n"
            "1. Main Topic: (one line)\n"
            "2. Target Audience: (one line)\n"
            "3. Emotional Tone: (one or two words)\n"
            "4. Content Angle / Promise: (one or two lines)\n"
            "5. Key Points or Benefits: (bullet-style list in plain text)\n"
            "Do NOT write a caption here. Only return the analysis.\n\n"
            f"<script>\n{script}\n</script>"
        ),
        agent = analyzer,
        expected_output=("A concise, structured analysis document following the requested five-section format. "
    "The content should be professional, insightful, and strictly limited to the required headers. "
    "Ensure the 'Key Points' are extracted accurately as actionable takeaways, and avoid unnecessary conversational filler or introductory sentences.")
    )

def writing(script: str, analysis: Task) -> Task:
    return Task(
        description=(
            "You are a master social media strategist. Your goal is to write a high-engagement "
            "caption that acts as a 'teaser' for the video script provided.\n\n"
            "Instructions:\n"
            "1. Start with a strong curiosity-driven hook based on the 'Content Angle' from the analysis.\n"
            "2. Provide one 'Value-Add' point—an extra tip, a startling statistic, or a piece of context "
            "not fully explored in the video. This ensures the audience feels they gain knowledge "
            "just by reading the caption.\n"
            "3. Frame the caption to be professional yet punchy for YouTube, Instagram, and Facebook.\n"
            "4. Constraint: Exactly 2-3 sentences. No emojis. No hashtags. No filler words.\n"
            "5. The final sentence must subtly encourage watching the video to master the concept.\n\n"
            f"<script>\n{script}\n</script>\n\n"
        ),
        expected_output=(
            "A high-value, 2-3 sentence caption that provides a unique insight or 'secret' "
            "related to the video topic, followed by a subtle call-to-action to watch the full content."
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

    analysis = analyzing(script)
    caption = writing(script=script, analysis=analysis)

    crew = Crew(agents=[analyzer, writer], tasks=[analysis, caption], process=Process.sequential) # Runs Task In A One After Another Sequence

    print("Generating Captions...\n")
    result = crew.kickoff()
    print("Analysis completed")
    print("Caption Generated: \n")
    print(result)

run()