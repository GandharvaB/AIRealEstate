import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	FileReadTool
)
from multi_agent_information_management_system_with_crew_supervision.tools.real_estate_api_tool import RealEstateApiTool
from multi_agent_information_management_system_with_crew_supervision.tools.property_analysis_scoring_tool import PropertyAnalysisScoringTool
from multi_agent_information_management_system_with_crew_supervision.tools.sarvam_property_analysis import SarvamPropertyAnalysisTool
from multi_agent_information_management_system_with_crew_supervision.tools.sarvam_api_response_generator import SarvamApiResponseGeneratorTool
from multi_agent_information_management_system_with_crew_supervision.tools.ninetynine_acres_tool import NinetyNineAcresApiTool
from multi_agent_information_management_system_with_crew_supervision.tools.magicbricks_tool import MagicBricksApiTool


@CrewBase
class MultiAgentInformationManagementSystemWithCrewSupervisionCrew:
    """MultiAgentInformationManagementSystemWithCrewSupervision crew"""

    
    @agent
    def real_estate_data_researcher(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["real_estate_data_researcher"],
            
            
            tools=[RealEstateApiTool(), NinetyNineAcresApiTool(), MagicBricksApiTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.3-70b-versatile",
                
                
            ),
            
        )
        
    
    @agent
    def property_development_analyst(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["property_development_analyst"],
            
            
            tools=[				PropertyAnalysisScoringTool(),
				SarvamPropertyAnalysisTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.3-70b-versatile",
                
                
            ),
            
        )
        
    
    @agent
    def api_response_manager(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["api_response_manager"],
            
            
            tools=[				SarvamApiResponseGeneratorTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.3-70b-versatile",
                
                
            ),
            
        )
        
    
    @agent
    def information_collector(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["information_collector"],
            
            
            tools=[				FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.3-70b-versatile",
                
                
            ),
            
        )
        
    
    @agent
    def client_presentation_specialist(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["client_presentation_specialist"],
            
            
            tools=[				FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.3-70b-versatile",
                
                
            ),
            
        )
        
    
    @agent
    def workflow_supervisor(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["workflow_supervisor"],
            
            
            tools=[				FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="groq/llama-3.3-70b-versatile",
                
                
            ),
            
        )
        
    

    
    @task
    def research_properties_data(self) -> Task:
        return Task(
            config=self.tasks_config["research_properties_data"],
            markdown=False,
            
            
        )
    
    @task
    def analyze_development_potential(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_development_potential"],
            markdown=False,
            
            
        )
    
    @task
    def generate_api_response(self) -> Task:
        return Task(
            config=self.tasks_config["generate_api_response"],
            markdown=False,
            
            
        )
    
    @task
    def collect_agent_information(self) -> Task:
        return Task(
            config=self.tasks_config["collect_agent_information"],
            markdown=False,
            
            
        )
    
    @task
    def format_client_presentation(self) -> Task:
        return Task(
            config=self.tasks_config["format_client_presentation"],
            markdown=False,
            
            
        )
    
    @task
    def supervise_and_monitor_workflow(self) -> Task:
        return Task(
            config=self.tasks_config["supervise_and_monitor_workflow"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the MultiAgentInformationManagementSystemWithCrewSupervision crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,

            chat_llm=LLM(model="openai/gpt-4o-mini"),
        )


