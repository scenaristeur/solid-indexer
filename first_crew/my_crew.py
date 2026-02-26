from crewai import Agent, Task, Crew

from albertLLM import AlbertLLM
import os
from dotenv import load_dotenv

base_url=os.getenv("OPENAI_BASE_URL")
api_key=os.getenv("OPENAI_API_KEY")
model = os.getenv("MODEL")

albert_llm = AlbertLLM(
    model=model,
    api_key=api_key,
    endpoint=base_url,
    temperature=0.7
)

# Use with an agent
agent = Agent(
    role="Research Assistant",
    goal="Find and analyze information",
    backstory="You are a research assistant.",
    llm=albert_llm
)

# Create and execute tasks
task = Task(
    description="Research the latest developments in AI",
    expected_output="A comprehensive summary",
    agent=agent
)

crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()