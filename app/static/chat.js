// Define uma função assíncrona porque vamos usar 'await' para esperar a resposta do backend
async function send() {
    const input = document.getElementById("msg");
    const userMessage = input.value.trim();

    if (!userMessage) return;

    // Desenha a mensagem do usuário
    appendMessage("Você", userMessage, "user-msg");
    input.value = "";

    // Cria o balão inicial com "Pensando..."
    const loadingDiv = appendMessage("IA", "Pensando...", "ai-msg", "loading");
    
    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage })
        });

        if (!res.ok) throw new Error("Falha na rede");

        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        
        let isFirstChunk = true;
        let fullText = "IA: ";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });

            // No primeiro pedaço de texto que chegar da IA:
            if (isFirstChunk) {
                // Remove a animação/estilo de loading imediatamente
                loadingDiv.classList.remove("loading");
                isFirstChunk = false;
            }

            // Acumula o texto e atualiza a div
            fullText += chunk;
            loadingDiv.textContent = fullText;

            // Rola o chat para o fim
            const chat = document.getElementById("chat");
            chat.scrollTop = chat.scrollHeight;
        }

    } catch (error) {
        // Se der erro, substitui o balão de carregamento pela mensagem de erro
        loadingDiv.textContent = "Erro: Falha ao se comunicar com o servidor.";
        loadingDiv.classList.remove("loading");
        loadingDiv.classList.add("error-msg");
    }
}

// Função auxiliar que recebe o nome do remetente, o texto e a classe CSS para o balão
function appendMessage(sender, text, ...classNames) {
    // Busca novamente o container principal do chat
    const chat = document.getElementById("chat");
    
    // Cria um novo elemento <div> na memória do navegador (ainda não aparece na tela)
    const msgDiv = document.createElement("div");

    // Adiciona as classes CSS a essa div. 
    // Ficará algo como: class="chat-bubble user-msg" ou class="chat-bubble ai-msg"
    msgDiv.classList.add("chat-bubble");
    
    // O operador ... permite adicionar múltiplos nomes de classe
    classNames.forEach(cls => {
        // Se a string contiver espaços (ex: "ai-msg loading"), divide e adiciona cada uma
        cls.split(" ").filter(Boolean).forEach(c => msgDiv.classList.add(c));
    });

    msgDiv.textContent = `${sender}: ${text}`;
    
    chat.appendChild(msgDiv);
    chat.scrollTop = chat.scrollHeight;

    return msgDiv; 
}