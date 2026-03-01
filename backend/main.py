import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# ... other imports

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # We use this to track the AI's current execution task
    state = {"active_loop": None, "process_tracker": {}} 
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # 1. THE KILL SWITCH
            if data.get("type") == "kill":
                if state["active_loop"] and not state["active_loop"].done():
                    state["active_loop"].cancel()
                    await websocket.send_json({"type": "error", "data": "SYSTEM: Execution manually terminated by user."})
                continue
            
            # 2. START TASK
            user_prompt = data.get("prompt")
            if user_prompt:
                # Cancel any existing loop before starting a new one
                if state["active_loop"] and not state["active_loop"].done():
                     state["active_loop"].cancel()
                     
                # Start the loop as an independent background task so we can still listen for "kill" signals
                state["active_loop"] = asyncio.create_task(
                    autonomous_worker_loop(user_prompt, websocket, session_id, state["process_tracker"])
                )
                
    except WebSocketDisconnect:
        if state["active_loop"]:
            state["active_loop"].cancel()
