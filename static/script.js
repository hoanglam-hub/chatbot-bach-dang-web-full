window.pastedImages = [];
let isLoading = false;
let currentController = null;

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("questionInput").addEventListener("paste", function(event) {
        const items = event.clipboardData.items;
        for (let item of items) {
            if (item.type.startsWith("image/")) {
                if (window.pastedImages.length >= 5) {
                    alert("Maximum 5 images per message!");
                    return;
                }
                const file = item.getAsFile();
                window.pastedImages.push(file);
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(e.target.result, window.pastedImages.length - 1);
                };
                reader.readAsDataURL(file);
                event.preventDefault();
            }
        }
    });
});

function showImagePreview(src, index) {
    let previewContainer = document.getElementById("previewContainer");
    if (!previewContainer) {
        previewContainer = document.createElement("div");
        previewContainer.id = "previewContainer";
        previewContainer.style.cssText = `
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            margin-bottom: 8px;
        `;
        const inputArea = document.querySelector(".input-area");
        inputArea.insertBefore(previewContainer, inputArea.firstChild);
    }

    const preview = document.createElement("div");
    preview.style.cssText = `position: relative; display: inline-block;`;
    preview.innerHTML = `
        <img src="${src}" style="height:60px; border-radius:6px;">
        <span onclick="removeOneImage(${index})" style="
            position: absolute;
            top: -5px; right: -5px;
            background: red;
            color: white;
            border-radius: 50%;
            width: 18px; height: 18px;
            text-align: center;
            cursor: pointer;
            font-size: 12px;
            line-height: 18px;
        ">✕</span>
    `;
    previewContainer.appendChild(preview);
}

function removeOneImage(index) {
    window.pastedImages.splice(index, 1);
    const container = document.getElementById("previewContainer");
    if (container) container.remove();
    window.pastedImages.forEach((file, i) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            showImagePreview(e.target.result, i);
        };
        reader.readAsDataURL(file);
    });
}

function removeAllPreviews() {
    const container = document.getElementById("previewContainer");
    if (container) container.remove();
    window.pastedImages = [];
}

async function sendMessage() {
    if (isLoading) return;

    const input = document.getElementById("questionInput");
    const question = input.value.trim();
    if (!question) return;

    isLoading = true;
    addMessage("user", question, window.pastedImages.slice());
    input.value = "";
    const loadingId = addLoading();

    const sendBtn = document.getElementById("sendBtn");
    const stopBtn = document.getElementById("stopBtn");
    if (sendBtn) sendBtn.style.display = "none";
    if (stopBtn) stopBtn.style.display = "inline-block";

    currentController = new AbortController();

    try {
        if (window.pastedImages.length > 0) {
            const formData = new FormData();
            formData.append("question", question);
            for (let img of window.pastedImages) {
                formData.append("images", img);
            }
            const response = await fetch("/chat_with_image", {
                method: "POST",
                body: formData,
                signal: currentController.signal
            });
            const data = await response.json();
            removeLoading(loadingId);
            addMessage("assistant", data.answer, []);
            removeAllPreviews();
        } else {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: question }),
                signal: currentController.signal
            });
            const data = await response.json();
            removeLoading(loadingId);
            addMessage("assistant", data.answer, []);
        }
    } catch (error) {
        removeLoading(loadingId);
        if (error.name === "AbortError") {
            addMessage("assistant", "Request cancelled.", []);
        } else {
            addMessage("assistant", "Sorry, an error occurred.", []);
        }
    } finally {
        isLoading = false;
        if (sendBtn) sendBtn.style.display = "inline-block";
        if (stopBtn) stopBtn.style.display = "none";
        currentController = null;
    }
}

function stopMessage() {
    if (currentController) {
        currentController.abort();
    }
}

function addMessage(role, text, images) {
    const chatBox = document.getElementById("chatBox");
    const div = document.createElement("div");
    div.className = `message ${role}`;

    const isUser = role === "user";
    const name = isUser ? "User" : "Chatbot";
    const avatarSrc = isUser ? "/static/user_avatar.png" : "/static/ngo_quyen.png";

    div.innerHTML = `
        <img src="${avatarSrc}" class="avatar">
        <div class="bubble">
            <div class="name">${name}</div>
            <div>${text}</div>
        </div>
    `;

    if (isUser && images && images.length > 0) {
        const bubble = div.querySelector(".bubble");
        images.forEach(file => {
            const url = URL.createObjectURL(file);
            const imgEl = document.createElement("img");
            imgEl.src = url;
            imgEl.style.cssText = "max-width:150px; border-radius:8px; margin-top:6px; display:block; cursor:pointer;";
            imgEl.onclick = function() {
                console.log("Image clicked, url:", url);
                showImageFromUrl(url);
            };
            bubble.appendChild(imgEl);
        });
    }

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

function showImageFromUrl(url) {
    let scale = 1;

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
    `;

    const img = document.createElement("img");
    img.src = url;
    img.style.cssText = `
        width: 60%;
        max-width: 800px;
        min-width: 400px;
        border-radius: 10px;
        box-shadow: 0 0 30px rgba(0,0,0,0.8);
        object-fit: contain;
        transition: transform 0.2s;
        cursor: default;
    `;

    // Nút điều khiển
    const controls = document.createElement("div");
    controls.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 12px;
        z-index: 1000;
    `;

    const btnStyle = `
        background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.4);
        color: white;
        font-size: 20px;
        width: 44px; height: 44px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    `;

    const zoomIn = document.createElement("button");
    zoomIn.innerHTML = "+";
    zoomIn.style.cssText = btnStyle;
    zoomIn.onclick = function(e) {
        e.stopPropagation();
        scale = Math.min(scale + 0.2, 3);
        img.style.transform = `scale(${scale})`;
    };

    const zoomOut = document.createElement("button");
    zoomOut.innerHTML = "−";
    zoomOut.style.cssText = btnStyle;
    zoomOut.onclick = function(e) {
        e.stopPropagation();
        scale = Math.max(scale - 0.2, 0.3);
        img.style.transform = `scale(${scale})`;
    };

    const reset = document.createElement("button");
    reset.innerHTML = "↺";
    reset.style.cssText = btnStyle;
    reset.onclick = function(e) {
        e.stopPropagation();
        scale = 1;
        img.style.transform = `scale(1)`;
    };

    const close = document.createElement("button");
    close.innerHTML = "✕";
    close.style.cssText = btnStyle;
    close.onclick = function(e) {
        e.stopPropagation();
        overlay.remove();
    };

    controls.appendChild(zoomOut);
    controls.appendChild(reset);
    controls.appendChild(zoomIn);
    controls.appendChild(close);

    overlay.appendChild(img);
    overlay.appendChild(controls);
    document.body.appendChild(overlay);

    // Nhấn vào nền để đóng
    overlay.onclick = function(e) {
        if (e.target === overlay) overlay.remove();
    };

    // Scroll chuột để zoom
    overlay.addEventListener("wheel", function(e) {
        e.preventDefault();
        if (e.deltaY < 0) {
            scale = Math.min(scale + 0.1, 3);
        } else {
            scale = Math.max(scale - 0.1, 0.3);
        }
        img.style.transform = `scale(${scale})`;
    });
}
