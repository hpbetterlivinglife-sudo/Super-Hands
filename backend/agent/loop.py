import asyncio
import json
from google import genai
import os
from tools.sandbox import execute_terminal_command
from agent.prompt import SYSTEM_PROMPT

# Setup Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def autonomous_worker_loop(user_task: str, websocket, session_id: str, process_tracker: dict):
    await websocket.send_json({"type": "status", "data": "Agent analyzing task with Gemini..."})
    
    history = f"Task: {user_task}\n"
    max_iterations = 10 
    current_iteration = 0
    
    while current_iteration < max_iterations:
        current_iteration += 1
        
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash', 
                contents=f"{SYSTEM_PROMPT}\n\nHistory:\n{history}\n\nWhat is your next step?"
            )
            
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            decision = json.loads(raw_text)
            
            await websocket.send_json({"type": "thought", "data": decision.get("thought", "")})
            
            if decision.get("action") == "execute_command":
                cmd = decision.get("command")
                await websocket.send_json({"type": "terminal_cmd", "data": f"$ {cmd}"})
                
                terminal_output = await execute_terminal_command(cmd, session_id, process_tracker)
                await websocket.send_json({"type": "terminal_out", "data": terminal_output})
                
                history += f"\n[Executed]: {cmd}\n[Result]: {terminal_output}\n"
                
            elif decision.get("action") == "finish":
                final_msg = decision.get("response_to_user", "Task Complete.")
                await websocket.send_json({"type": "agent_msg", "data": final_msg})
                break
                
        except Exception as e:
            await websocket.send_json({"type": "error", "data": f"Gemini Error: {str(e)}"})
            break
