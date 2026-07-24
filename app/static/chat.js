async function send() {

    const input = document.getElementById("msg");

    const res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            message: input.value
        })
    });

    const data = await res.json();

    document.getElementById("chat").innerHTML += `
        <p><b>Você:</b> ${input.value}</p>
        <p><b>IA:</b> ${data.response}</p>
    `;

    input.value = "";
}