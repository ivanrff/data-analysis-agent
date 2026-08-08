from langchain.agents import create_agent
from langchain_groq import ChatGroq
# from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os
from app.tools.tools import tools
from langgraph.checkpoint.memory import InMemorySaver
from collections import OrderedDict

load_dotenv()

groq_chat = ChatGroq(
    model="qwen/qwen3.6-27b",
    temperature=0,
    api_key=os.getenv('GROQ_API_KEY'),
    max_tokens=1000
)

# ollama_chat = ChatOllama(
#     model="qwen3.5:latest",
#     temperature=0
# )

system_prompt = """
    Sua tarefa é auxiliar os colaboradores internos da empresa BimBam Buy.

    Você possui duas fontes de informação:
    1. `buscar_docs`: Para buscar REGRAS, POLÍTICAS e TEXTOS (Ex: "Como funciona a garantia?", "Quais as formas de pagamento?").
    2. `consultar_vendas_sql`: Para buscar NÚMEROS, MÉTRICAS e TABELAS no DuckDB (Ex: "Qual o produto mais vendido?", "Quantas vendas fiz em maio?").

    Diretrizes de Roteamento:
    - Se a pergunta for conceitual/textual -> Use `buscar_docs`.
    - Se a pergunta exigir cálculos ou dados de tabelas -> Use `consultar_vendas_sql`.
    - Sempre formate meses usando o nome dos meses e semanas usando o nome dos dias da semana.
    - Ao dar respostas textuais sobre receitas ou venda, formate o valor no padrão de moeda.
    - Traduza o nome das categorias para português sempre que possível.

    - Se o usuário perguntar algo fora do escopo da empresa -> Responda com seu conhecimento prévio educadamente, sem usar ferramentas.
    - NUNCA invente dados numéricos. Se a ferramenta de SQL retornar vazio, diga que não encontrou os dados na base.
    
    - SE O USUÁRIO PEDIR UM GRÁFICO: Formate a resposta OBRIGATORIAMENTE em um bloco de código markdown com a linguagem 'json-chart'.
    
    Exemplo de formato esperado para gráficos (padrão Plotly):
    ```json-chart
    {
        "data": [{
            "x": ["Produto A", "Produto B"],
            "y": [150, 300],
            "type": "bar",
            "marker": { "color": "#f12a7c" }
        }],
        "layout": {
            "title": "Vendas por Produto"
        }
    }
    ```
    """

MAX_SESSIONS = 5  # limite de conversas simultâneas guardadas em memória

checkpointer = InMemorySaver()
active_threads = OrderedDict()  # controla quais threads estão "vivas"

def touch_thread(thread_id: str):
    """Marca a thread como usada recentemente; remove a mais antiga se estourar o limite."""
    if thread_id in active_threads:
        active_threads.move_to_end(thread_id)
    else:
        active_threads[thread_id] = True
        if len(active_threads) > MAX_SESSIONS:
            oldest_id, _ = active_threads.popitem(last=False)
            checkpointer.delete_thread(oldest_id)

agent = create_agent(
    model=groq_chat,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=checkpointer,
    debug=True
)