from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent import agent

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    async def event_generator():
        # Usa a API de streaming assíncrona do agente
        stream = await agent.astream_events(
            {"messages": [{"role": "user", "content": req.message}]},
            version="v3"
        )
        # Itera sobre as mensagens geradas pelo modelo em tempo real
        async for message in stream.messages:
            async for delta in message.text:
                if delta:
                    # Envia cada pedaço (chunk) de texto para o cliente
                    yield delta

    return StreamingResponse(event_generator(), media_type="text/plain; charset=utf-8")

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")