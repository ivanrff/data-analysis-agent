from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agent import agent

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    print("Invoking agent...")
    response = agent.invoke({"messages": [{"role": "user", "content": req.message}]})
    # print(response["messages"][-1].content_blocks)
    res_content = response.get("messages")[-1].to_json()["kwargs"]["content"]
    return {"response": res_content}

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
# uv run uvicorn app.main:app --reload