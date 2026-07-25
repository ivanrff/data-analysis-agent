// Define a função assíncrona responsável por enviar a mensagem do usuário e processar a resposta da IA
async function send() {
    // Busca a caixa de texto onde o usuário digita pelo ID "msg"
    const input = document.getElementById("msg");

    // Captura o texto digitado e remove espaços desnecessários no início e no fim (.trim())
    const userMessage = input.value.trim();

    // Se o usuário não digitou nada (ou apenas espaços), encerra a execução da função imediatamente
    if (!userMessage) return;

    // Desenha na tela a mensagem digitada pelo usuário usando a classe "user-msg"
    appendMessage("Você", userMessage, "user-msg");

    // Limpa o campo de texto de entrada para que o usuário possa digitar a próxima mensagem
    input.value = "";

    // Cria o balão inicial da IA exibindo "Pensando..." com o estilo "loading" e guarda a referência da div
    const loadingDiv = appendMessage("IA", "Pensando...", "ai-msg", "loading");
    
    // Inicia o bloco try/catch para capturar falhas de rede ou no servidor durante o fetch
    try {
        // Envia a requisição HTTP POST para a rota /chat da API FastAPI
        const res = await fetch("/chat", {
            method: "POST", // Define o método da requisição como POST
            headers: { "Content-Type": "application/json" }, // Informa ao backend que o corpo é um objeto JSON
            body: JSON.stringify({ message: userMessage }) // Converte o objeto JavaScript em uma string JSON
        });

        // Se a resposta HTTP retornar um status de erro (ex: 404 ou 500), lança uma exceção
        if (!res.ok) throw new Error("Falha na rede");

        // Obtém o leitor de fluxo (stream) para consumir a resposta do servidor em tempo real
        const reader = res.body.getReader();

        // Instancia o decodificador para converter os dados binários recebidos em texto UTF-8
        const decoder = new TextDecoder("utf-8");
        
        // Define uma flag para identificar o momento exato em que o primeiro pedaço de texto chegar
        let isFirstChunk = true;

        // Inicializa a variável que vai acumular o texto total exibido no balão da IA
        let fullText = "IA: ";

        // Inicia um loop infinito para ler o fluxo de dados continuamente enquanto houver resposta
        while (true) {
            // Lê o próximo pedaço de dados vindo do servidor; 'done' é true quando o fluxo termina
            const { value, done } = await reader.read();

            // Se o servidor finalizou o envio do fluxo, interrompe o loop while
            if (done) break;

            // Transforma os bytes recebidos em uma string legível
            const chunk = decoder.decode(value, { stream: true });

            // Executa esta verificação apenas no primeiro pedaço de texto que a IA enviar
            if (isFirstChunk) {
                // Remove a classe CSS de "loading", tirando o estilo/animação de "Pensando..."
                loadingDiv.classList.remove("loading");

                // Marca a flag como falsa para não executar esse bloco nos pedaços seguintes
                isFirstChunk = false;
            }

            // Concatena o novo trecho recebido ao texto acumulado
            fullText += chunk;

            // Atualiza o conteúdo visual do balão de texto com o novo acumulado em tempo real
            loadingDiv.textContent = fullText;

            // Busca o container principal do chat
            const chat = document.getElementById("chat");

            // Rola a barra de rolagem do chat para a parte inferior mantendo as novas mensagens visíveis
            chat.scrollTop = chat.scrollHeight;
        }

    } catch (error) {
        // Se ocorrer qualquer erro, limpa o estado de carregamento e insere a mensagem de falha no balão
        loadingDiv.textContent = "Erro: Falha ao se comunicar com o servidor.";

        // Remove a classe "loading" para parar qualquer indicação visual de progresso
        loadingDiv.classList.remove("loading");

        // Adiciona a classe "error-msg" para estilizar o balão com visual de erro (ex: texto vermelho)
        loadingDiv.classList.add("error-msg");
    }
}

// Função auxiliar que cria elementos HTML na tela para representar os balões de mensagem
function appendMessage(sender, text, ...classNames) {
    // Busca o elemento container do chat na página pelo seu ID
    const chat = document.getElementById("chat");
    
    // Cria um novo elemento <div> na memória DOM
    const msgDiv = document.createElement("div");

    // Aplica a classe base padrão "chat-bubble" no novo elemento
    msgDiv.classList.add("chat-bubble");
    
    // Percorre a lista de classes adicionais passadas nos parâmetros (...classNames)
    classNames.forEach(cls => {
        // Divide caso passe nomes compostos (ex: "ai-msg loading") e adiciona cada classe individualmente
        cls.split(" ").filter(Boolean).forEach(c => msgDiv.classList.add(c));
    });

    // Define o conteúdo em texto da div (ex: "Você: Olá" ou "IA: Pensando...")
    msgDiv.textContent = `${sender}: ${text}`;
    
    // Insere a div recém-criada como filha do container principal do chat para aparecer na página
    chat.appendChild(msgDiv);

    // Ajusta o scroll para rolar até o final da página e exibir o novo balão
    chat.scrollTop = chat.scrollHeight;

    // Retorna a referência do elemento criado para que possa ser atualizado mais tarde durante o streaming
    return msgDiv; 
}