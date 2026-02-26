import os
from crewai import Agent, Task, Crew, LLM
# Importing crewAI tools
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)
from crewai.rag.embeddings.providers.openai.types import OpenAIProviderSpec
from crewai_tools.tools.rag import RagToolConfig

# Set up API keys
# os.environ["SERPER_API_KEY"] = "Your Key" # serper.dev API key
from dotenv import load_dotenv

base_url=os.getenv("OPENAI_BASE_URL")
api_key=os.getenv("OPENAI_API_KEY")
model = os.getenv("MODEL")
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
    reasoning_effort="medium"  # For o1 models: low, medium, high
)


# https://docs.crewai.com/en/tools/ai-ml/ragtool#openai
embedding_model: OpenAIProviderSpec = {
    "provider": "openai",
    "config": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model_name": "openweight-embeddings",
        "dimensions": 1536,
        "organization_id": "your-org-id",
        "api_base": os.getenv("OPENAI_BASE_URL"),
        "api_version": "v1",
        "default_headers": {"Custom-Header": "value"}
    }
}

config: RagToolConfig = {
    # "vectordb": vectordb,
    "embedding_model": embedding_model
}

# Instantiate tools
docs_tool = DirectoryReadTool(directory='./blog-posts')
file_tool = FileReadTool()
# search_tool = SerperDevTool()
# web_rag_tool = WebsiteSearchTool(config=config)

# Create agents
researcher = Agent(
    role='Market Research Analyst',
    goal='Provide up-to-date market analysis of the AI industry',
    backstory='An expert analyst with a keen eye for market trends.',
    # tools=[search_tool, web_rag_tool],
    # tools=[ web_rag_tool],
    verbose=True
)

writer = Agent(
    role='Content Writer',
    goal='Craft engaging blog posts about the AI industry',
    backstory='A skilled writer with a passion for technology.',
    tools=[docs_tool, file_tool],
    verbose=True
)

# Define tasks
research = Task(
    description='Research the latest trends in the AI industry and provide a summary.',
    expected_output='A summary en Français of the top 3 trending developments in the AI industry with a unique perspective on their significance.',
    agent=researcher
)

write = Task(
    description="Write an engaging blog post about the AI industry, based on the research analyst's summary. Draw inspiration from the latest blog posts in the directory.",
    expected_output='A 4-paragraph blog post formatted in markdown with engaging, informative, and accessible content, avoiding complex jargon. En français',
    agent=writer,
    output_file='blog-posts/new_post.md'  # The final blog post will be saved here
)

# Assemble a crew with planning enabled
crew = Crew(
    agents=[researcher, writer],
    tasks=[research, write],
    verbose=True,
    planning=True,  # Enable planning feature
)

# Execute tasks
crew.kickoff()