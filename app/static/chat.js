// Define uma função assíncrona porque vamos usar 'await' para esperar a resposta do backend
async function send() {
    // Busca a caixa de texto onde o usuário digita a mensagem pelo ID "msg"
    const input = document.getElementById("msg");

    // Busca a div principal onde as mensagens do chat são exibidas
    const chat = document.getElementById("chat");

    // Pega o texto digitado e remove espaços vazios inúteis no início e no fim (.trim())
    const userMessage = input.value.trim();

    // Se o usuário não digitou nada (ou só apertou espaço), interrompe a função aqui mesmo
    if (!userMessage) return;

    // 1. Chama nossa função auxiliar para desenhar a mensagem do usuário na tela imediatamente
    // Passamos o remetente ("Você"), o texto e a classe CSS ("user-msg") para estilizar a bolha
    appendMessage("Você", userMessage, "user-msg");

    // Limpa o campo de texto para o usuário poder digitar a próxima mensagem
    input.value = "";

    // Inicia um bloco try/catch para tratar possíveis erros de conexão com a API
    try {
        // Faz a requisição POST para a rota /chat do seu FastAPI e espera (await) a resposta
        const res = await fetch("/chat", {
            method: "POST", // Define o método HTTP como POST
            headers: { "Content-Type": "application/json" }, // Avisa ao FastAPI que o corpo é um JSON
            body: JSON.stringify({ message: userMessage }) // Converte o objeto JS para uma string JSON
        });

        // Converte o corpo da resposta recebida do servidor em um objeto JS
        const data = await res.json();
        
        // 2. Chama a função auxiliar para desenhar a resposta da IA na tela
        // Usamos a classe "ai-msg" para podermos estilizar a bolha da IA diferente da do usuário
        appendMessage("IA", data.response, "ai-msg");

    } catch (error) {
        // Se houver algum erro de rede ou o servidor cair, cai aqui e exibe uma mensagem de erro
        appendMessage("Erro", "Falha ao se comunicar com o servidor.", "error-msg");
    }
}

// Função auxiliar que recebe o nome do remetente, o texto e a classe CSS para o balão
function appendMessage(sender, text, className) {
    // Busca novamente o container principal do chat
    const chat = document.getElementById("chat");
    
    // Cria um novo elemento <div> na memória do navegador (ainda não aparece na tela)
    const msgDiv = document.createElement("div");

    // Adiciona as classes CSS a essa div. 
    // Ficará algo como: class="chat-bubble user-msg" ou class="chat-bubble ai-msg"
    msgDiv.classList.add("chat-bubble", className);
    
    // Define o texto dentro da div de forma segura. 
    // O .textContent garante que o texto seja tratado como texto puro, evitando falhas de segurança (XSS)
    msgDiv.textContent = `${sender}: ${text}`;
    
    // Anexa a nova div como filha dentro do container principal do chat (coloca ela no final da lista)
    chat.appendChild(msgDiv);
    
    // Faz o container do chat rolar automaticamente até o fundo para mostrar a mensagem mais recente
    chat.scrollTop = chat.scrollHeight;
}