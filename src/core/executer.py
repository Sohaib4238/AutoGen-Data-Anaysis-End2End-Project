import os
import logging
from autogen.coding import DockerCommandLineCodeExecutor

logger = logging.getLogger(__name__)

def get_docker_executor():    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    work_dir = os.path.abspath(os.path.join(base_dir, "temp_workspace"))
    
    os.makedirs(work_dir, exist_ok=True)
    
    logger.info(f"Mapping Docker workspace to: {work_dir}")

    executor = DockerCommandLineCodeExecutor(
        image="amancevice/pandas:2.2.2",
        timeout=60,  
        work_dir=work_dir
    )
    
    return executor, work_dir