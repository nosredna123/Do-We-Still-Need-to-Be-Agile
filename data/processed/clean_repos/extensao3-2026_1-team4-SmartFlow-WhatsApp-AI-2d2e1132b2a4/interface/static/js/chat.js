document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');

    let messageHistory = [];
    const iaId = 1; // ID padrão, pode ser alterado via seletor

    const addMessage = (text, sender) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.innerHTML = `<p>${text}</p>`;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const handleSendMessage = async () => {
        const text = messageInput.value.trim();
        if (text && !sendButton.disabled) {
            addMessage(text, 'user');
            messageHistory.push({ role: 'user', content: text });
            messageInput.value = '';
            sendButton.disabled = true;
            messageInput.disabled = true;

            try {
                // Chamar o endpoint /api/chat
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: text,
                        ia_id: iaId,
                        history: messageHistory
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    addMessage(data.response, 'bot');
                    messageHistory.push({ role: 'assistant', content: data.response });
                } else {
                    const errorMsg = data.error || 'Erro desconhecido ao processar mensagem';
                    addMessage(`❌ ${errorMsg}`, 'bot');
                }
            } catch (error) {
                console.error('Erro ao conectar no backend:', error);
                addMessage('❌ Erro ao conectar no servidor. Verifique se o backend está rodando.', 'bot');
            } finally {
                sendButton.disabled = false;
                messageInput.disabled = false;
                messageInput.focus();
            }
        }
    };

    sendButton.addEventListener('click', handleSendMessage);

    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !sendButton.disabled) {
            handleSendMessage();
        }
    });
});
