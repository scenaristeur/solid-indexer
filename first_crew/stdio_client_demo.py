# crewai with mcp server https://docs.crewai.com/en/mcp/overview

from crewai import Agent, Task, Crew, LLM
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

# from albertLLM import AlbertLLM
import os
import warnings
from dotenv import load_dotenv
from pydantic import PydanticDeprecatedSince20

warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

base_url=os.getenv("OPENAI_BASE_URL")
api_key=os.getenv("OPENAI_API_KEY")
model = os.getenv("MODEL_LARGE_ALIAS2")

print(base_url, api_key, model)


llm = LLM(
    model=model,
    api_key=api_key,
    base_url=base_url,  # Optional custom endpoint
    organization="org-...",  # Optional organization ID
    project="proj_...",  # Optional project ID
    temperature=0.7,
    max_tokens=128000,
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
    reasoning_effort="medium",  # For o1 models: low, medium, high
    # strict=False
)

server_params = StdioServerParameters(
    command="python3",
    args=["servers/math_server.py"],
    env={"UV_PYTHON": "3.12", **os.environ}
)

with MCPServerAdapter(server_params) as tools:
    print(f"Available tools from Stdio MCP server: {[tool.name for tool in tools]}")

    # Use with an agent
    agent = Agent(
        role="Mathematician",
        goal="Perform mathematical operations",
        backstory="An experiences mathematician that can perform mathematical operation with MCP tools.",
        llm=llm,
        tools=tools,
        verbose=True,
    )

    # agent = Agent(
    #     role="Research Assistant",
    #     goal="Find and analyze information",
    #     backstory="You are a research assistant.",
    #     llm=albert_llm
    # )
    # Create and execute tasks
    task = Task(
        description="Solve the math {problem} given to you by the user.",
        expected_output="The correct answer to the math problem using the available tools.",
        agent=agent
    )

    # task = Task(
    #     description="Research the latest developments in AI",
    #     expected_output="A comprehensive summary",
    #     agent=agent
    # )
    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    result = crew.kickoff(inputs={"problem": "sqrt(2.25)"})
    print(result)