import asyncio
import docker
import os

# Connect to the Docker daemon on your VPS
client = docker.from_env()

# Create a workspace directory on your VPS host if it doesn't exist
WORKSPACE_DIR = os.path.abspath("./agent_workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

def get_or_create_sandbox(session_id: str):
    """Ensures a persistent, isolated Docker container is running for this session."""
    container_name = f"super_hands_sandbox_{session_id}"
    try:
        container = client.containers.get(container_name)
        if container.status != "running":
            container.start()
        return container
    except docker.errors.NotFound:
        # Spin up a fresh Ubuntu container, keeping it alive, and mounting our workspace
        return client.containers.run(
            "ubuntu:latest",
            name=container_name,
            command="tail -f /dev/null", # Keeps the container running forever
            detach=True,
            volumes={WORKSPACE_DIR: {'bind': '/workspace', 'mode': 'rw'}},
            working_dir="/workspace"
        )

async def execute_terminal_command(command: str, session_id: str, process_tracker: dict) -> str:
    """Runs a shell command safely INSIDE the Docker sandbox."""
    container = get_or_create_sandbox(session_id)
    
    try:
        # We use asyncio to run the blocking Docker command in a separate thread
        # This prevents the FastAPI server from freezing
        loop = asyncio.get_event_loop()
        
        # We execute using bash inside the container
        exec_command = ["bash", "-c", command]
        
        def run_exec():
            # Run the command and get the exec stream
            exit_code, output = container.exec_run(exec_command, stream=False)
            return exit_code, output.decode('utf-8')

        # Track the task so we can kill it if needed
        task = loop.run_in_executor(None, run_exec)
        process_tracker['current_task'] = task 
        
        exit_code, output = await task
        
        if exit_code != 0:
             return f"EXECUTION FAILED (Exit Code {exit_code}):\n{output}"
        
        return output.strip() if output.strip() else "Command executed successfully."

    except Exception as e:
        return f"SANDBOX ERROR: {str(e)}"
