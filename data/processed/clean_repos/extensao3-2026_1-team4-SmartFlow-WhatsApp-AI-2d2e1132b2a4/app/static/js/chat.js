document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const messageInput = document.getElementById("message-input");
    const chatForm = document.getElementById("chat-form");
    const sendButton = document.getElementById("send-button");
    const iaIdInput = document.getElementById("ia-id-input");
    const statusText = document.getElementById("connection-status");
    const selectedIaLabel = document.getElementById("selected-ia-label");
    const clearChatButton = document.getElementById("clear-chat-button");
    const newChatButton = document.getElementById("new-chat-button");
    const switchIaCard = document.getElementById("switch-ia-card");
    const suggestionButtons = document.querySelectorAll(".suggestion");

    if (!chatMessages || !messageInput || !chatForm || !sendButton || !iaIdInput || !statusText) {
        console.error("Elementos essenciais do chat nao foram encontrados.");
        return;
    }

    const histories = new Map();

    const getIaId = () => {
        const iaId = Number.parseInt(iaIdInput.value, 10);
        return Number.isInteger(iaId) && iaId > 0 ? iaId : 1;
    };

    const getHistory = (iaId) => {
        if (!histories.has(iaId)) {
            histories.set(iaId, []);
        }

        return histories.get(iaId);
    };

    const addMessage = (text, sender, isError = false) => {
        const shouldStickToBottom =
            chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight < 120;

        const message = document.createElement("div");
        message.classList.add("message", sender);

        if (isError) {
            message.classList.add("error");
        }

        message.textContent = text;
        chatMessages.appendChild(message);

        if (shouldStickToBottom || sender === "user") {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    };

    const renderWelcome = () => {
        const iaId = getIaId();
        iaIdInput.value = iaId;
        chatMessages.replaceChildren();
        statusText.textContent = `IA ID ${iaId} selecionada`;
        if (selectedIaLabel) {
            selectedIaLabel.textContent = `ID ${iaId}`;
        }
        addMessage(`Olá! Você está conversando com a IA de ID ${iaId}.`, "bot");
    };

    const setLoading = (isLoading) => {
        sendButton.disabled = isLoading;
        messageInput.disabled = isLoading;
        iaIdInput.disabled = isLoading;

        const buttonText = sendButton.querySelector("span");
        if (buttonText) {
            buttonText.textContent = isLoading ? "Enviando" : "Enviar";
        }
    };

    const startNewChat = () => {
        histories.set(getIaId(), []);
        renderWelcome();
        messageInput.value = "";
        messageInput.focus();
    };

    const sendMessage = async () => {
        const text = messageInput.value.trim();
        const iaId = getIaId();

        if (!text) {
            return;
        }

        const history = getHistory(iaId);
        addMessage(text, "user");
        history.push({ role: "user", content: text });
        messageInput.value = "";
        setLoading(true);

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: text,
                    ia_id: iaId,
                    history
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                const errorMessage = data.error || "Nao foi possivel processar a mensagem.";
                history.pop();
                addMessage(errorMessage, "bot", true);
                return;
            }

            addMessage(data.response, "bot");
            history.push({ role: "assistant", content: data.response });

            if (data.ia_name) {
                statusText.textContent = `${data.ia_name} - IA ID ${iaId}`;
            }
        } catch (error) {
            console.error("Erro ao conectar no backend:", error);
            history.pop();
            addMessage("Erro ao conectar no servidor FastAPI.", "bot", true);
        } finally {
            setLoading(false);
            messageInput.focus();
        }
    };

    chatForm.addEventListener("submit", (event) => {
        event.preventDefault();
        sendMessage();
    });

    messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            chatForm.requestSubmit();
        }
    });

    iaIdInput.addEventListener("change", renderWelcome);

    clearChatButton?.addEventListener("click", startNewChat);
    newChatButton?.addEventListener("click", startNewChat);
    switchIaCard?.addEventListener("click", () => {
        iaIdInput.focus();
        iaIdInput.select();
    });

    suggestionButtons.forEach((button) => {
        button.addEventListener("click", () => {
            messageInput.value = button.textContent.trim();
            messageInput.focus();
        });
    });

    renderWelcome();
});


