async function sendMessage() {
    const input = document.getElementById("questionInput");
    const question = input.value.trim();
    if (!question) return;

    addMessage("user", question, null);
    input.value = "";

    const loadingId = addLoading();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question })
        });
        const data = await response.json();

        removeLoading(loadingId);

        addMessage("assistant", data.answer, data.image);

    } catch (error) {
        removeLoading(loadingId);
        addMessage("assistant", "Xin lỗi, có lỗi xảy ra.", null);
    }
}

function addMessage(role, text, imageBase64) {
    const chatBox = document.getElementById("chatBox");
    const div = document.createElement("div");
    div.className = `message ${role}`;

    const isUser = role === "user";
    const name = isUser ? "User" : "Chatbot";
    const avatarSrc = isUser ? "/static/user_avatar.png" : "/static/ngo_quyen.png";

    let imageHTML = "";
    if (imageBase64) {
        imageHTML = `<img src="data:image/png;base64,${imageBase64}" class="generated-image">`;
    }

    div.innerHTML = `
        <img src="${avatarSrc}" class="avatar">
        <div class="bubble">
            <div class="name">${name}</div>
            <div>${text}</div>
            ${imageHTML}
        </div>
    `;

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addLoading() {
    const chatBox = document.getElementById("chatBox");
    const div = document.createElement("div");
    const id = "loading_" + Date.now();
    div.id = id;
    div.className = "message assistant";
    div.innerHTML = `
        <img src="/static/ngo_quyen.png" class="avatar">
        <div class="bubble">
            <div class="name">Chatbot</div>
            <div>Thinking...</div>
        </div>
    `;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

function removeLoading(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function handleKeyPress(event) {
    if (event.key === "Enter") sendMessage();
}

function showImage(src, alt) {
    const overlay = document.createElement("div");
    overlay.style.cssText = `
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0,0,0,0.8);
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    `;

    const img = document.createElement("img");
    img.src = src;
    img.alt = alt;
    img.style.cssText = `
        max-width: 80%;
        max-height: 80%;
        border-radius: 10px;
        box-shadow: 0 0 30px rgba(0,0,0,0.8);
    `;

    overlay.appendChild(img);
    document.body.appendChild(overlay);

    overlay.onclick = () => overlay.remove();
}