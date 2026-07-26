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
    Você é o assistente inteligente da BimBam Buy.

    Você possui duas fontes de informação:
    1. `buscar_docs`: Para buscar REGRAS, POLÍTICAS e TEXTOS (Ex: "Como funciona a garantia?", "Quais as formas de pagamento?").
    2. `consultar_dados_sql`: Para buscar NÚMEROS, MÉTRICAS e TABELAS no DuckDB (Ex: "Qual o produto mais vendido?", "Quantas vendas fiz em maio?").

    Diretrizes de Roteamento:
    - Se a pergunta for conceitual/textual -> Use `buscar_docs`.
    - Se a pergunta exigir cálculos ou dados de tabelas -> Use `consultar_dados_sql`.
    - Se o usuário perguntar algo fora do escopo da empresa -> Responda com seu conhecimento prévio educadamente, sem usar ferramentas.
    - NUNCA invente dados numéricos. Se a ferramenta de SQL retornar vazio, diga que não encontrou os dados na base.
"""

agent = create_agent(
    model=ollama_chat,
    tools=tools,
    system_prompt=system_prompt,
    # debug=True
)