"""
src/core/orchestrator.py
Assembles the agents and enforces the Round Robin pipeline with strict error handling.
"""
import os
import logging
import autogen
from dotenv import load_dotenv
from src.agents.agent_work import AgentFactory
from src.core.executer import get_docker_executor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class DataAnalyzerPipeline:
    def __init__(self, user_query: str, filename: str):
        """Initializes the pipeline state."""
        self.user_query = user_query
        self.filename = filename
        
        self.llm_config = {
            "config_list": [{
                "model": "llama-3.1-70b-versatile", 
                "api_key": os.environ.get("GROQ_API_KEY"),
                "base_url": "https://api.groq.com/openai/v1"
            }],
            "temperature": 0.1,
        }
        
        self.executor = None
        self.work_dir = None

    def execute(self):
        """Runs the full round-robin pipeline with strict error handling."""
        try:
            logger.info("Initializing Docker Sandbox...")
            self.executor, self.work_dir = get_docker_executor()

            logger.info("Instantiating AI Agent Team via Factory...")
            factory = AgentFactory(self.llm_config)
            team = factory.create_data_team()

            admin_proxy = autogen.UserProxyAgent(
                name="Admin",
                human_input_mode="NEVER",
                code_execution_config={"executor": self.executor},
                is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", "").upper(),
                max_consecutive_auto_reply=15,
            )

            logger.info("Configuring Round Robin Group Chat...")
            groupchat = autogen.GroupChat(
                agents=[
                    admin_proxy,
                    team["loader"],
                    team["cleaner"],
                    team["engineer"],
                    team["analyzer"],
                    team["visualizer"],
                    team["reporter"]
                ],
                messages=[],
                max_round=20, 
                speaker_selection_method="round_robin"
            )

            manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=self.llm_config)

            logger.info(f"Starting analysis on {self.filename}...")
            
            initial_message = f"""
            The user has uploaded a dataset. It is located in your workspace as '{self.filename}'.
            The user's analytical query is: '{self.user_query}'
            
            DataLoader, begin by loading the file and inspecting it.
            """

            # Executing the pipeline
            result = admin_proxy.initiate_chat(manager, message=initial_message)
            
            logger.info("Pipeline completed successfully.")
            return result

        except Exception as e:
            logger.error(f"Pipeline crashed during execution: {str(e)}", exc_info=True)
            raise 
        finally:
            if self.executor:
                logger.info("Stopping Docker container to free system resources...")
                self.executor.stop()