import asyncio
import json
from google import genai
from tools.sandbox import execute_terminal_command
from agent.prompt import SYSTEM_PROMPT

# Initialize the Gemini client
client = genai.Client()

async def autonomous_worker_loop(user_task: str, websocket, session_id: str, process_tracker: dict):
    """The real Plan-Act-Verify recursive loop."""
    
    await websocket.send_json({"type": "status", "data": "Agent analyzing task..."})
    
    history = f"Task: {user_task}\n"
    max_iterations = 10 
    current_iteration = 0
    
    while current_iteration < max_iterations:
        current_iteration += 1
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=f"{SYSTEM_PROMPT}\n\nHistory:\n{history}\n\nWhat is your next step?"
            )
            
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            decision = json.loads(raw_text)
            
            await websocket.send_json({"type": "thought", "data": decision.get("thought", "")})
            
            if decision.get("action") == "execute_command":
                cmd = decision.get("command")
                await websocket.send_json({"type": "terminal_cmd", "data": f"$ {cmd}"})
                
                # The Sandbox requires the session_id and process_tracker to work!
                terminal_output = await execute_terminal_command(cmd, session_id, process_tracker)
                await websocket.send_json({"type": "terminal_out", "data": terminal_output})
                
                history += f"\n[Executed]: {cmd}\n[Result]: {terminal_output}\n"
                
            elif decision.get("action") == "finish":
                final_msg = decision.get("response_to_user", "Task Complete.")
                await websocket.send_json({"type": "agent_msg", "data": final_msg})
                break
                
        except json.JSONDecodeError:
            await websocket.send_json({"type": "status", "data": "Agent output invalid JSON. Retrying..."})
            history += f"\n[System Error]: You did not output valid JSON. Try again.\n"
            
        except asyncio.CancelledError:
            # This catches the Kill Switch signal and stops the loop gracefully
            raise
            
        except Exception as e:
            await websocket.send_json({"type": "error", "data": str(e)})
            break
            
    if current_iteration >= max_iterations:
        await websocket.send_json({"type": "error", "data": "Max iterations reached. Agent paused to prevent infinite loop."})
