from langchain.agents import create_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv('GROQ_API_KEY'),
)

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="Você é um assistente útil.",
    debug=True
)