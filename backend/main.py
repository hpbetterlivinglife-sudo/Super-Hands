import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from agent.loop import autonomous_worker_loop

# 1. Initialize the FastAPI server (This is what was missing!)
app = FastAPI(title="Super Hands OS")

# 2. Allow your Next.js UI to connect without security blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "Super Hands Backend is Online"}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print(f"Session {session_id} connected.")
    
    # We use this to track the AI's current execution task for the Kill Switch
    state = {"active_loop": None, "process_tracker": {}} 
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # THE KILL SWITCH
            if data.get("type") == "kill":
                if state["active_loop"] and not state["active_loop"].done():
                    state["active_loop"].cancel()
                    await websocket.send_json({"type": "error", "data": "SYSTEM: Execution manually terminated by user."})
                continue
            
            # START AI TASK
            user_prompt = data.get("prompt")
            if user_prompt:
                # Cancel any existing loop before starting a new one
                if state["active_loop"] and not state["active_loop"].done():
                     state["active_loop"].cancel()
                     
                # Start the loop as an independent background task
                state["active_loop"] = asyncio.create_task(
                    autonomous_worker_loop(user_prompt, websocket, session_id, state["process_tracker"])
                )
                
    except WebSocketDisconnect:
        print(f"Session {session_id} disconnected.")
        if state["active_loop"]:
            state["active_loop"].cancel()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
