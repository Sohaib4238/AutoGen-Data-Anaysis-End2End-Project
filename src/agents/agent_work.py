import autogen
from src.agents.prompts import (
    DATA_LOADER_PROMPT,
    DATA_CLEANER_PROMPT,
    FEATURE_ENGINEER_PROMPT,
    DATA_ANALYZER_PROMPT,
    VISUALIZER_PROMPT,
    REPORT_GENERATOR_PROMPT,
)

class AgentWork:
    def __init__(self, llm_config):
        self.llm_config = llm_config

    def create_data_team(self) -> dict:
        loader = autogen.AssistantAgent(
            name="DataLoader",
            system_message=DATA_LOADER_PROMPT,  
            llm_config=self.llm_config
        )
        cleaner = autogen.AssistantAgent(
            name="DataCleaner",
            system_message=DATA_CLEANER_PROMPT,  
            llm_config=self.llm_config
        )
        engineer = autogen.AssistantAgent(
            name="FeatureEngineer",
            system_message=FEATURE_ENGINEER_PROMPT,  
            llm_config=self.llm_config
        )
        analyzer = autogen.AssistantAgent(
            name="DataAnalyzer",
            system_message=DATA_ANALYZER_PROMPT,  
            llm_config=self.llm_config
        )
        visualizer = autogen.AssistantAgent(
            name="Visualizer",
            system_message=VISUALIZER_PROMPT,  
            llm_config=self.llm_config
        )
        reporter = autogen.AssistantAgent(
            name="ReportGenerator",
            system_message=REPORT_GENERATOR_PROMPT,  
            llm_config=self.llm_config
        )
        return {
            "loader": loader,
            "cleaner": cleaner,
            "engineer": engineer,
            "analyzer": analyzer,
            "visualizer": visualizer,
            "reporter": reporter
        }