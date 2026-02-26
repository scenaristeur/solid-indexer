import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
# from solid_auth import SolidAuthenticatedSession
from albertLLM import AlbertLLM

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


@CrewBase
class FirstCrew():
    """FirstCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True,
            llm=llm
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True,
            llm=llm
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the FirstCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
