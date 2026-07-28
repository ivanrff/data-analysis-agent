from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from app.agent import agent_with_history


app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

@app.post("/chat")
async def chat(req: ChatRequest):
    async def event_generator():
        # Change version to "v2" and remove the 'await' from the call
        stream_generator = agent_with_history.astream_events(
            {"messages": [{"role": "user", "content": req.message}]},
            config={"configurable": {"session_id": req.session_id}},
            version="v2" # <--- FIXED VERSION HERE
        )
        
        async for event in stream_generator:
            if event["event"] == "on_chat_model_stream":
                chunk_data = event["data"]["chunk"].content
                
                if chunk_data and isinstance(chunk_data, str):
                    yield chunk_data

    return StreamingResponse(event_generator(), media_type="text/plain; charset=utf-8")

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")