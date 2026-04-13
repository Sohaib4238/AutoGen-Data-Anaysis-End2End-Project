import os
import autogen 
from autogen.coding import DockerCommandLineCodeExecutor

def get_executer():
    work_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../temp_workspace"))
    os.makedirs(work_dir, exist_ok=True)

    excuter = DockerCommandLineCodeExecutor(
        image="amancevice/pandas:2.2.2",
        timeout=60,
        work_dir=work_dir
    )

    return excuter, work_dir