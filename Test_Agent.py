import os
from crewai import Agent, Task, Crew, Process, LLM

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




# Defininng Basic Caption Agent

agent = Agent(role="Reel Caption Writer", 
              goal=("Read the provided video script and write a concise, high-converting caption that works on YouTube, Instagram, and Facebook."),
              backstory=("You are an expert social media copywriter who deeply understands hooks, audience psychology, and platform best practices for YouTube, Instagram, and Facebook."),
              llm=llm,
              verbose=True) # This Prints What The Agent Is Thinking

# Defining Task For Agent

def writing(script: str) -> Task:
    return Task(
        description=(
            "You are given a video script between <script> and </script>.\n"
            "1. Understand the main topic and emotion.\n"
            "2. Write ONE simple caption (1-2 sentences) that would make people curious.\n"
            "3. The caption must work for YouTube, Instagram, and Facebook.\n"
            "4. Do NOT add emojis\n"
            "Return only the final caption.\n\n"
            f"<script>\n{script}\n</script>"
        ),
        expected_output="A single concise caption that summarizes the video script, give additional info(if any) and sparks curiosity.",
        agent=agent,
    )

# Making Them A Crew And Running

def run():
    script = get_script()
    print("Script Recieved...\n")
    print(f"Agent Started For Script... {script[:30]} \n")
    caption_task = writing(script)

    crew = Crew(agents=[agent], tasks=[caption_task], process=Process.sequential) # Runs Task In A One After Another Sequence

    print("Generating Captions...\n")
    result = crew.kickoff()
    print("Caption Generated: \n")
    print(result)

run()