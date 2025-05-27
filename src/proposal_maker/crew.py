from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool, FileReadTool
from typing import List
import os
from dotenv import load_dotenv
load_dotenv()
import agentops
agentops.init()
from .models import (
    ExtractedContent, EvaluationReport,
    RequirementsList, PersonasList, UserGoalsList, UserStoriesList,
    RequirementMappingsList, CritiqueReport
)

llm1 = LLM(
        model="gemini/gemini-2.5-flash-preview-04-17",
        temperature=0.3,
        # stream=True,
        api_key=os.getenv("GEMINI_API_KEY"),  # Set your Google API key here
        reasoning_effort="high",  # Optional, can be set to "low", "medium", or "high"
    )
@CrewBase
class ProposalMaker():
    """ProposalMaker crew"""

    @before_kickoff
    def before_kickoff_function(self, inputs):
        print(f"Before kickoff function with inputs: {inputs}")
        inputs['company_name'] = input("Enter the company name:\n")
        inputs['date'] = input("Enter the current year:\n")
        inputs['user_name'] = input("Enter your name:\n")
        inputs['company_overview'] = input("Enter a brief company overview:\n")
        print(f"Before kickoff function with inputs: {inputs}")

        return inputs # You can return the inputs or modify them as needed

    agents: List[BaseAgent]
    tasks: List[Task]

    # Agents
    @agent
    def document_reader(self) -> Agent:
        return Agent(
            config=self.agents_config['document_reader'], # type: ignore[index]
            verbose=True,
            tools=[FileReadTool(file_path="knowledge/Request for Proposal.txt")],
        )

    @agent
    def requirements_classifier(self) -> Agent:
        return Agent(
            config=self.agents_config['requirements_classifier'], # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool(
                n_results=40,
                search_type="search",
            )],
        )
    
    @agent
    def persona_generator(self) -> Agent:
        """Agent to create user personas."""
        return Agent(
            config=self.agents_config['persona_generator'],
            tools=[SerperDevTool(
                n_results=30,
                search_type="search",
            )],
            verbose=True
        )

    @agent
    def goal_identifier(self) -> Agent:
        """Agent to identify user goals."""
        return Agent(
            config=self.agents_config['goal_identifier'],
            verbose=True
        )

    @agent
    def requirement_mapper(self) -> Agent:
        """Agent to map requirements to goals."""
        return Agent(
            config=self.agents_config['requirement_mapper'],
            verbose=True
        )

    @agent
    def story_generator(self) -> Agent:
        """Agent to generate user stories."""
        return Agent(
            config=self.agents_config['story_generator'],
            tools=[SerperDevTool(
                n_results=30,
                search_type="search",
            )],
            verbose=True
        )

    @agent
    def markdown_creator(self) -> Agent:
        """Agent to create markdown documentation."""
        return Agent(
            config=self.agents_config['markdown_creator'],
            verbose=True,
            llm=llm1,  # Use the LLM instance defined above
            # allow_delegation=True  # Allow delegation to other agents if needed
        )

    @agent
    def evaluator(self) -> Agent:
        """Agent to evaluate outputs."""
        return Agent(
            config=self.agents_config['evaluator'],
            verbose=True,
        )
    
    @agent
    def tech_stack_recommender(self) -> Agent:
        """Agent to research technology stack."""
        return Agent(
            config=self.agents_config['tech_stack_recommender'],
            verbose=True,
            # allow_delegation=True  # Allow delegation to other agents if needed
        )

    @agent
    def internet_researcher(self) -> Agent:
        """Agent to research differentiating factors and strengths for the proposal."""
        return Agent(
            config=self.agents_config['internet_researcher'],
            tools=[SerperDevTool(
                n_results=50,
                search_type="search",
            )],
            verbose=True,
            llm=llm1,  # Use the LLM instance defined above
        )

    @agent
    def cost_calculator(self) -> Agent:
        """Agent to calculate project cost."""
        return Agent(
            config=self.agents_config['cost_calculator'],
            verbose=True,
            llm=llm1,  # Use the LLM instance defined above
        )

    @agent
    def conclusion_writer(self) -> Agent:
        """Agent to write formal conclusion and fetch contact details from webpage."""
        return Agent(
            config=self.agents_config['conclusion_writer'],
            tools=[SerperDevTool(
                n_results=50,
                search_type="search",
            )],
            verbose=True
        )

    @agent
    def critique(self) -> Agent:
        """Agent to critique the final proposal against the RFP."""
        return Agent(
            config=self.agents_config['critique'],
            verbose=True
        )

    @agent
    def refinement(self) -> Agent:
        """Agent to refine the proposal based on critique feedback."""
        return Agent(
            config=self.agents_config['refinement'],
            verbose=True,
            llm=llm1,  # Use the LLM instance defined above
        )

    # Tasks
    @task
    def extract_content(self) -> Task:
        return Task(
            config=self.tasks_config['extract_content'], # type: ignore[index]
            tools=[FileReadTool(
                    file_path="knowledge/Request for Proposal.txt"
                ),  # Optional, you can add tools to your task
            ],
            output_pydantic=ExtractedContent,  # Specify the output type
            output_file='output/json/extracted_content.json',  # Specify the output file
        )
    
    @task
    def classify_requirements(self) -> Task:
        
        """Classify extracted requirements."""
        return Task(
            config=self.tasks_config['classify_requirements'],
            output_pydantic=RequirementsList,
            output_file='output/json/requirements.json'
        )

    @task
    def generate_personas(self) -> Task:
        """Generate user personas."""
        return Task(
            config=self.tasks_config['generate_personas'],
            output_pydantic=PersonasList,
            output_file='output/json/personas.json'
        )

    @task
    def identify_user_goals(self) -> Task:
        """Identify user goals for each persona."""
        return Task(
            config=self.tasks_config['identify_user_goals'],
            output_pydantic=UserGoalsList,
            output_file='output/json/user_goals.json'
        )

    @task
    def map_requirements(self) -> Task:
        """Map requirements to user goals."""
        return Task(
            config=self.tasks_config['map_requirements'],
            output_pydantic=RequirementMappingsList,
            output_file='output/json/requirements_mapping.json'
        )

    @task
    def generate_user_stories(self) -> Task:
        """Generate user stories."""
        return Task(
            config=self.tasks_config['generate_user_stories'],
            tools=[SerperDevTool(
                n_results=30,
                search_type="search",
            )],
            output_pydantic=UserStoriesList,
            output_file='output/json/user_stories.json'
        )
    
    @task
    def generate_technical_report(self) -> Task:
        """Generate technical report."""
        serperdevtool = SerperDevTool(
            n_results=50,
            search_type="search",
            # search_engine="serperdev"  # Optional, specify if you want to use a specific search engine
        )
        return Task(
            config=self.tasks_config['generate_technical_report'],
            tools=[serperdevtool],
            output_file='output/intermediate_md/technical_report.md',
            markdown=True,  # Specify that this task outputs markdown

        )
    
    @task
    def generate_differentiation_analysis(self) -> Task:
        """Conduct internet research for differentiating factors and strengths."""
        return Task(
            config=self.tasks_config['generate_differentiation_analysis'],
            tools=[SerperDevTool(
                n_results=50,
                search_type="search",
            )],
            output_file='output/intermediate_md/differentiation_analysis.md',
            markdown=True,  # Specify that this task outputs markdown

        )

    @task
    def calculate_project_cost(self) -> Task:
        """Calculate the total project cost."""
        return Task(
            config=self.tasks_config['calculate_project_cost'],
            output_file='output/intermediate_md/project_cost.md',
            markdown=True,  # Specify that this task outputs markdown
        )

    @task
    def write_conclusion(self) -> Task:
        """Draft a formal conclusion with contact details."""
        return Task(
            config=self.tasks_config['write_conclusion'],
            tools=[SerperDevTool(
                n_results=10,
                search_type="search",
            )],
            output_file='output/intermediate_md/conclusion.md',
            markdown=True,  # Specify that this task outputs markdown
        )

    @task
    def create_final_proposal(self) -> Task:
        """Create final proposal documentation."""
        return Task(
            config=self.tasks_config['create_final_proposal'],
            markdown=True,  # Specify that this task outputs markdown
            output_file='output/final_md/proposal.md',
        )

    @task
    def evaluate_output(self) -> Task:
        """Evaluate all generated artifacts."""
        return Task(
            config=self.tasks_config['evaluate_output'],
            output_pydantic=EvaluationReport,
            output_file='output/json/evaluation_report.json'
        )

    @task
    def critique_proposal(self) -> Task:
        """Task to critique the final proposal against the RFP."""
        return Task(
            config=self.tasks_config['critique_proposal'],
            output_pydantic=CritiqueReport,
            output_file='output/json/critique_report.json',
        )

    @task
    def refine_proposal(self) -> Task:
        """Task to refine the proposal based on critique feedback."""
        return Task(
            config=self.tasks_config['refine_proposal'],
            output_file='output/final_md/refined_proposal.md',
            markdown=True,  # Specify that this task outputs markdown,
            human_input=True
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ProposalMaker crew"""


        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
            max_rpm=30
        )
