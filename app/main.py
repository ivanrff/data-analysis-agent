from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

from app.agent import agent

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

@app.post("/chat")
@limiter.limit("10/hour")
async def chat(request: Request, req: ChatRequest):
    async def event_generator():
        recursion_count = 0
        # Change version to "v2" and remove the 'await' from the call
        stream_generator = agent.astream_events(
            {"messages": [{"role": "user", "content": req.message}]},
            config={
                "configurable": {"thread_id": req.session_id},
                "recursion_limit": 4
            },
            version="v2"
        )

        async for event in stream_generator:
            if event["event"] in ["on_chat_model_start", "on_tool_start"]:
                recursion_count += 1
                print(f"[DEBUG] Step {recursion_count}: {event['name']}")

            if event["event"] == "on_chat_model_stream":
                chunk_data = event["data"]["chunk"].content
                if chunk_data and isinstance(chunk_data, str):
                    yield chunk_data

        print(f"[METRICS] Total agent steps for session {req.session_id}: {recursion_count}")

    return StreamingResponse(event_generator(), media_type="text/plain; charset=utf-8")

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")