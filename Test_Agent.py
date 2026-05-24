import os
from crewai import Agent, Task, Crew, Process, LLM

key = os.getenv("GEMINI_API_KEY")
if not key:
    raise ValueError("Gemini Key Not Available Or Read By Agent")

llm = LLM("gemini/gemini-3.1-flash-lite", api_key=key)

# Sample Script For Testing

script = '''जेठ के महीने में पड़ने वाले मंगल को बड़ा मंगल क्यों कहते हैं। 

वैसे तो हर मंगलवार हनुमान जी का दिन होता हैं लेकिन जेठ महीने में पड़ने वाले मंगलवार को मुख्यतः दो कारणों से बड़ा मंगल कहते हैं।

पहला ये कि मान्यता के अनुसार इसी महीने के किसी मंगलवार के दिन हनुमान जी महाराज भगवान राम से पहली बार मिले थे जिस कारण इस महीने को उनके जीवन का सबसे खास महीना माना जाता है।

दूसरा ये कि जेठ के महीने में भीषण गर्मी पड़ती है जिस वजह से इस महीने अन्न जल बांटने से न सिर्फ लोगों को राहत मिलती है बल्कि हनुमान जी के माध्यम से किया हुआ पुण्य और ज़्यादा सफल हो जाता है।

पहला धार्मिक और दूसरा तार्किक कारण है, लेकिन आप किस शहर से वीडियो देख रहे हैं और क्या वहां बड़ा मंगल मनाया जाता है, हमें नीचे कमेंट करके ज़रूर बताइएगा।
'''

# Defininng Basic Caption Agent

agent = Agent(role="Basic Caption Agent", 
              goal="Read the provided video script and write a single concise caption that works on YouTube, Instagram and Facebook.",
              backstory=("You are an expert social media copywriter who writes clear, engaging captions that summarize the core idea and make people curious."),
              llm=llm,
              verbose=True) # This Prints What The Agent Is Thinking

# Defining Task For Agent

caption_task = Task(
    description=(
        "You are given a video script between <script> and </script>.\n"
        "1. Understand the main topic and emotion.\n"
        "2. Write ONE simple caption (1-2 sentences) that would make people curious.\n"
        "3. The caption must work for YouTube, Instagram, and Facebook.\n"
        "4. Do NOT add hashtags or emojis.\n"
        "Return only the caption text.\n\n"
        f"<script>\n{script}\n</script>"
    ),
    expected_output="A single concise caption that summarizes the video script, give additional info(if any) and sparks curiosity.",
    agent=agent,
)

# Making Them A Crew And Running

def run():
    print("Script Recieved...\n")
    print(f"Agent Started For Script... {script[:30]} \n")

    crew = Crew(agents=[agent], tasks=[caption_task], process=Process.sequential) # Runs Task In A One After Another Sequence

    print("Generating Captions...\n")
    result = crew.kickoff()
    print("Caption Generated: \n")
    print(result)

run()