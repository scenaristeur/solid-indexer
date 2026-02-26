from crewai import Agent, Task, Crew, LLM

# from albertLLM import AlbertLLM
import os
from dotenv import load_dotenv

base_url=os.getenv("OPENAI_BASE_URL")
api_key=os.getenv("OPENAI_API_KEY")
model = os.getenv("MODEL")
# model ="albert-large"

llm = LLM(
    model=model,
    api_key=api_key,
    base_url=base_url,  # Optional custom endpoint
    organization="org-...",  # Optional organization ID
    project="proj_...",  # Optional project ID
    temperature=0.7,
    max_tokens=4000,
    max_completion_tokens=4000,  # For newer models
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
    stop=["END"],
    seed=42,  # For reproducible outputs
    stream=True,  # Enable streaming
    timeout=60.0,  # Request timeout in seconds
    max_retries=3,  # Maximum retry attempts
    logprobs=True,  # Return log probabilities
    top_logprobs=5,  # Number of most likely tokens
    reasoning_effort="medium"  # For o1 models: low, medium, high
)

# Use with an agent
agent = Agent(
    role="Research Assistant",
    goal="Find and analyze information",
    backstory="You are a research assistant.",
    llm=llm
)

# Create and execute tasks
task = Task(
    description="Research the latest developments in AI",
    expected_output="A comprehensive summary",
    agent=agent
)

crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()