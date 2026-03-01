import asyncio
import json
import os
from google import genai
from tools.sandbox import execute_terminal_command
from agent.prompt import SYSTEM_PROMPT

# Initialize the Gemini client (Make sure GEMINI_API_KEY is in your VPS environment variables)
# export GEMINI_API_KEY="your-api-key-here"
client = genai.Client()

async def autonomous_worker_loop(user_task: str, websocket):
    """The real Plan-Act-Verify recursive loop."""
    
    await websocket.send_json({"type": "status", "data": "Agent analyzing task..."})
    
    # We maintain the conversation history so the AI remembers what it just did
    history = f"Task: {user_task}\n"
    
    max_iterations = 10 # Safety switch to prevent infinite loops on your server
    current_iteration = 0
    
    while current_iteration < max_iterations:
        current_iteration += 1
        
        try:
            # 1. Ask Gemini what to do next
            response = client.models.generate_content(
                model='gemini-2.5-flash', # Fast and great at coding/JSON
                contents=f"{SYSTEM_PROMPT}\n\nHistory:\n{history}\n\nWhat is your next step?"
            )
            
            # Parse the JSON response
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            decision = json.loads(raw_text)
            
            # Stream the AI's thought to the UI
            await websocket.send_json({"type": "thought", "data": decision.get("thought", "")})
            
            # 2. ACT: Execute the command
            if decision.get("action") == "execute_command":
                cmd = decision.get("command")
                await websocket.send_json({"type": "terminal_cmd", "data": f"$ {cmd}"})
                
                # The "Hands" touch the VPS
                terminal_output = await execute_terminal_command(cmd)
                await websocket.send_json({"type": "terminal_out", "data": terminal_output})
                
                # 3. VERIFY: Append the result to the history so Gemini can read it on the next loop
                history += f"\n[Executed]: {cmd}\n[Result]: {terminal_output}\n"
                
            # 4. FINISH: Task complete
            elif decision.get("action") == "finish":
                final_msg = decision.get("response_to_user", "Task Complete.")
                await websocket.send_json({"type": "agent_msg", "data": final_msg})
                break
                
        except json.JSONDecodeError:
            error_msg = "Agent output invalid JSON. Retrying..."
            await websocket.send_json({"type": "status", "data": error_msg})
            history += f"\n[System Error]: You did not output valid JSON. Try again.\n"
            
        except Exception as e:
            await websocket.send_json({"type": "error", "data": str(e)})
            break
            
    if current_iteration >= max_iterations:
        await websocket.send_json({"type": "error", "data": "Max iterations reached. Agent paused to prevent infinite loop."})
