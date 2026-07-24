from langchain.tools import tool

@tool
def saber_o_clima(cidade: str) -> str:
    """
    Retorna o clima para a cidade solicitada.
    """
    return f"É sempre ensolarado em {cidade}"

@tool
def saber_a_temperatura(cidade: str) -> str:
    """
    Retorna a temperatura para a cidade solicitada.
    """
    return f"Agora faz 27°C em {cidade}"

tools = [saber_o_clima, saber_a_temperatura]