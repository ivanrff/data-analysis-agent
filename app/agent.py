from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os
from app.tools.tools import tools

load_dotenv()

groq_chat = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv('GROQ_API_KEY'),
)

ollama_chat = ChatOllama(
    model="qwen3.5:latest",
    temperature=0
)

system_prompt = """
    Você é um assistente meteorológico.
    Use a ferramenta `saber_o_clima` se o usuário perguntar o clima.
    Use a ferramenta `saber_a_temperatura` se o usuário perguntar a temperatura.
    """

agent = create_agent(
    model=ollama_chat,
    tools=tools,
    system_prompt=system_prompt
)