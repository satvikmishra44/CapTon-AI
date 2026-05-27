import os
from textwrap import shorten
from crewai import Agent, Task, Crew, Process, LLM
from ddgs import DDGS
import json


key = os.getenv("GEMINI_API_KEY")
if not key:
    raise ValueError("Gemini Key Not Available Or Read By Agent")

llm = LLM("gemini/gemini-3.1-flash-lite", api_key=key)

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
