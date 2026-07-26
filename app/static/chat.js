// Async function to send the user message and process the AI response
async function send() {
    const input = document.getElementById("msg");
    const userMessage = input.value.trim();

    if (!userMessage) return;

    appendMessage("Você", userMessage, "user-msg");
    input.value = "";

    // Create initial AI bubble indicating loading state
    const loadingDiv = appendMessage("AI", "Pensando...", "ai-msg", "loading");
    
    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage })
        });

        if (!res.ok) throw new Error("Erro de conexão com o servidor.");

        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        
        let isFirstChunk = true;
        let fullText = "AI: ";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });

            if (isFirstChunk) {
                loadingDiv.classList.remove("loading");
                isFirstChunk = false;
            }

            fullText += chunk;
            loadingDiv.textContent = fullText;

            const chat = document.getElementById("chat");
            chat.scrollTop = chat.scrollHeight;
        }

    } catch (error) {
        loadingDiv.textContent = "Error: Falha na conexão com o servidor.";
        loadingDiv.classList.remove("loading");
        loadingDiv.classList.add("error-msg");
    }
}

// Helper function to create chat bubbles
function appendMessage(sender, text, ...classNames) {
    const chat = document.getElementById("chat");
    const msgDiv = document.createElement("div");

    msgDiv.classList.add("chat-bubble");
    
    classNames.forEach(cls => {
        cls.split(" ").filter(Boolean).forEach(c => msgDiv.classList.add(c));
    });

    msgDiv.textContent = `${sender}: ${text}`;
    
    chat.appendChild(msgDiv);
    chat.scrollTop = chat.scrollHeight;

    return msgDiv; 
}

// Allow pressing "Enter" to trigger the send function
document.getElementById("msg").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        send();
    }
});