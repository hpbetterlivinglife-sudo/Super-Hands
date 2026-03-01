import asyncio
import json
from openai import OpenAI
import os
from tools.sandbox import execute_terminal_command
from agent.prompt import SYSTEM_PROMPT

# 1. Setup OpenRouter Client
# We use the OpenAI library because OpenRouter follows the same format
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

async def autonomous_worker_loop(user_task: str, websocket, session_id: str, process_tracker: dict):
    await websocket.send_json({"type": "status", "data": "Agent analyzing task with OpenRouter..."})
    
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    history.append({"role": "user", "content": f"Task: {user_task}"})
    
    max_iterations = 10 
    current_iteration = 0
    
    while current_iteration < max_iterations:
        current_iteration += 1
        
        try:
            # 2. Call the OpenRouter Free Model
            response = client.chat.completions.create(
                model="arcee-ai/trinity-large-preview:free",
                messages=history
            )
            
            content = response.choices[0].message.content
            # Clean the JSON if the model adds markdown backticks
            raw_text = content.strip().replace("```json", "").replace("```", "")
            decision = json.loads(raw_text)
            
            await websocket.send_json({"type": "thought", "data": decision.get("thought", "")})
            
            if decision.get("action") == "execute_command":
                cmd = decision.get("command")
                await websocket.send_json({"type": "terminal_cmd", "data": f"$ {cmd}"})
                
                terminal_output = await execute_terminal_command(cmd, session_id, process_tracker)
                await websocket.send_json({"type": "terminal_out", "data": terminal_output})
                
                # Add the result to memory for the next loop
                history.append({"role": "assistant", "content": content})
                history.append({"role": "user", "content": f"Command Result: {terminal_output}"})
                
            elif decision.get("action") == "finish":
                final_msg = decision.get("response_to_user", "Task Complete.")
                await websocket.send_json({"type": "agent_msg", "data": final_msg})
                break
                
        except Exception as e:
            await websocket.send_json({"type": "error", "data": f"Brain Error: {str(e)}"})
            break
