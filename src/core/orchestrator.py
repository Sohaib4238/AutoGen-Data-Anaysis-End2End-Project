"""
src/core/orchestrator.py
Assembles the agents and enforces the Round Robin pipeline with strict error handling.
"""
import os
import logging
import autogen
from dotenv import load_dotenv
from src.agents.agent_work import AgentWork
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
                # Using the newest active Gemini model
                "model": "gemini-2.5-flash", 
                "api_key": os.environ.get("GEMINI_API_KEY"),
                # This secret URL routes the OpenAI client directly to Google!
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/" 
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
            factory = AgentWork(self.llm_config)
            team = factory.create_data_team()

            admin_proxy = autogen.UserProxyAgent(
                name="Admin",
                human_input_mode="NEVER",
                code_execution_config={"executor": self.executor},
                is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", "").upper(),
                max_consecutive_auto_reply=15,
            )

            logger.info("Configuring State Machine Group Chat...")
            
            # --- THE ENTERPRISE ROUTER ---
            def state_machine_router(last_speaker, groupchat):
                """Forces a strict sequential pipeline and guarantees Docker execution."""
                messages = groupchat.messages
                
                # Rule 0: If it is the very first message from Admin, start with DataLoader.
                if len(messages) == 1:
                    return team["loader"]
                
                # Rule 1: If an AI agent just wrote code, the Admin MUST execute it next.
                ai_coders = [team["loader"], team["cleaner"], team["engineer"], team["analyzer"], team["visualizer"]]
                if last_speaker in ai_coders:
                    return admin_proxy
                
                # Rule 2: If the Admin just executed code, figure out who goes next.
                if last_speaker == admin_proxy:
                    if len(messages) >= 2:
                        prev_speaker = messages[-2]["name"]
                        if prev_speaker == "DataLoader": return team["cleaner"]
                        if prev_speaker == "DataCleaner": return team["engineer"]
                        if prev_speaker == "FeatureEngineer": return team["analyzer"]
                        if prev_speaker == "DataAnalyzer": return team["visualizer"]
                        if prev_speaker == "Visualizer": return team["reporter"]
                
                # Rule 3: If the reporter finishes, end the chat.
                if last_speaker == team["reporter"]:
                    return None 
            # -----------------------------

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
                speaker_selection_method=state_machine_router # <--- Inject the custom logic here
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