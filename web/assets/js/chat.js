const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const loadingSpinner = document.getElementById('loading-spinner');
const conversationList = document.getElementById('conversation-list');
const newChatButton = document.getElementById('new-chat-button');
const startButton = document.getElementById('start-button');
const chatControlsContainer = document.getElementById('chat-controls-container');
const infoMessageBox = document.getElementById('infoMessageBox');
const menuButton = document.getElementById('hamburger-menu');
const sidebar = document.querySelector('.sidebar');

const originalMessagePlaceholder = messageInput.placeholder;

let currentConversationId = window.currentConversationId;
let initialHistory = window.initialHistory;

startButton.addEventListener('click', () => { window.location.href = '/'; });

function disableControls() {
    messageInput.disabled = true;
    sendButton.disabled = true;
    messageInput.placeholder = "Thinking...";
}

function enableControls() {
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.placeholder = originalMessagePlaceholder;
    messageInput.focus();
}

function addMessage(text, sender) {
    if (infoMessageBox && !infoMessageBox.classList.contains('hidden')) {
        infoMessageBox.classList.add('hidden');
    }

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    const textSpan = document.createElement('span');
    textSpan.textContent = text;

    if (sender === 'bot') {
        const aeonIcon = document.createElement('img');
        aeonIcon.src = '/assets/img/aeon-icon.png';
        aeonIcon.alt = 'Aeon Icon';
        aeonIcon.classList.add('aeon-message-icon');
        
        messageDiv.appendChild(aeonIcon);
        messageDiv.appendChild(textSpan);

    } else if (sender === 'user') {
        const userAvatarCanvas = document.createElement('canvas');
        userAvatarCanvas.classList.add('user-message-avatar');
        if (currentConversationId && currentConversationId !== 'None') {
            generateAvatar(userAvatarCanvas, currentConversationId);
        } else {
            generateAvatar(userAvatarCanvas, "default-user-seed"); 
        }
        messageDiv.appendChild(textSpan);
        messageDiv.appendChild(userAvatarCanvas);
    }
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const userMessage = messageInput.value.trim();
    if (userMessage === '') return;

    addMessage(userMessage, 'user');
    messageInput.value = '';
    
    loadingSpinner.style.display = 'block';
    chatBox.appendChild(loadingSpinner);
    chatBox.scrollTop = chatBox.scrollHeight;
    disableControls();

    try {
        const payload = { message: userMessage };
        if (currentConversationId && currentConversationId !== 'None') { 
            payload.conversation_id = currentConversationId;
        }

        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        
        loadingSpinner.style.display = 'none';
        
        if (response.ok) {
            addMessage(data.response, 'bot');
            if (data.conversation_id && data.conversation_id !== currentConversationId) {
                currentConversationId = data.conversation_id;
                window.history.pushState({}, '', `/chat/${currentConversationId}`);
                loadConversations();
            }
        } else {
            addMessage(data.response, 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('An error occurred. Please try again.', 'bot');
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls();
    }
}

async function loadConversations() {
    try {
        const response = await fetch('/conversations');
        const conversations = await response.json();
        
        conversationList.innerHTML = '';
        if (conversations.length > 0) {
            if (infoMessageBox) infoMessageBox.classList.add('hidden');

            conversations.forEach(conv => {
                const listItem = document.createElement('li');
                listItem.classList.add('conversation-item');
                listItem.setAttribute('data-id', conv.id);

                const userAvatarCanvas = document.createElement('canvas');
                userAvatarCanvas.classList.add('user-message-avatar');
                generateAvatar(userAvatarCanvas, conv.id);
                
                userAvatarCanvas.addEventListener('click', () => {
                    window.location.href = `/chat/${conv.id}`;
                });

                listItem.appendChild(userAvatarCanvas);

                const conversationName = document.createElement('span');
                conversationName.textContent = conv.name;
                conversationName.addEventListener('click', () => {
                    window.location.href = `/chat/${conv.id}`;
                });
                listItem.appendChild(conversationName);

                const deleteButton = document.createElement('button');
                deleteButton.classList.add('delete-conversation-button');
                deleteButton.innerHTML = `
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5 20C5 20.5304 5.21071 21.0391 5.58579 21.4142C5.96086 21.7893 6.46957 22 7 22H17C17.5304 22 18.0391 21.7893 18.4142 21.4142C18.7893 21.0391 19 20.5304 19 20V8H5V20ZM16 5H18V7H6V5H8L10 3H14L16 5ZM3 7H21V8H3V7Z"/>
                    </svg>
                `;
                deleteButton.addEventListener('click', (event) => {
                    event.stopPropagation();
                    deleteConversation(conv.id);
                });
                listItem.appendChild(deleteButton);

                if (currentConversationId && currentConversationId !== 'None' && conv.id === currentConversationId) {
                    listItem.classList.add('active');
                }
                conversationList.appendChild(listItem);
            });
            chatControlsContainer.classList.remove('hidden');
            enableControls();
        } else {
            if (infoMessageBox) infoMessageBox.classList.remove('hidden');
            const listItem = document.createElement('li');
            listItem.textContent = 'No conversations found.';
            conversationList.appendChild(listItem);
            chatControlsContainer.classList.add('hidden');
            disableControls();
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
        if (infoMessageBox) infoMessageBox.classList.remove('hidden');
        const listItem = document.createElement('li');
        listItem.textContent = 'Failed to load conversations.';
        conversationList.appendChild(listItem);
        chatControlsContainer.classList.add('hidden');
        disableControls();
    }
}

async function deleteConversation(convIdToDelete) {
    const userConfirmed = await new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'confirm-modal';
        modal.innerHTML = `
            <div class="confirm-modal-content">
                <p>Are you sure you want to delete this conversation? This action cannot be undone.</p>
                <div class="confirm-modal-buttons">
                    <button id="confirm-yes">Yes</button>
                    <button id="confirm-no">No</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById('confirm-yes').onclick = () => {
            document.body.removeChild(modal);
            resolve(true);
        };
        document.getElementById('confirm-no').onclick = () => {
            document.body.removeChild(modal);
            resolve(false);
        };
    });

    if (!userConfirmed) {
        return;
    }

    loadingSpinner.style.display = 'block';
    disableControls();
    try {
        const response = await fetch(`/delete_conversation/${convIdToDelete}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            if (currentConversationId === convIdToDelete) {
                currentConversationId = null;
                window.location.href = '/';
            } else {
                loadConversations();
            }
        } else {
            const data = await response.json();
            const messageBox = document.createElement('div');
            messageBox.className = 'info-message-box';
            messageBox.textContent = data.message || 'Failed to delete conversation.';
            chatBox.appendChild(messageBox);
            setTimeout(() => chatBox.removeChild(messageBox), 3000);
        }
    } catch (error) {
        console.error('Error deleting conversation:', error);
        const messageBox = document.createElement('div');
        messageBox.className = 'info-message-box';
        messageBox.textContent = 'An error occurred during deletion.';
        chatBox.appendChild(messageBox);
        setTimeout(() => chatBox.removeChild(messageBox), 3000);
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls();
    }
}

async function startNewChat() {
    loadingSpinner.style.display = 'block';
    disableControls();
    
    try {
        const response = await fetch('/new_chat', { method: 'POST' });
        const data = await response.json();
        
        if (response.ok) {
            window.location.href = `/chat/${data.conversation_id}`;
        } else {
            addMessage(data.message || 'Failed to create new chat.', 'bot');
            if (infoMessageBox) infoMessageBox.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error starting new chat:', error);
        addMessage('An error occurred trying to start a new chat.', 'bot');
        if (infoMessageBox) infoMessageBox.classList.add('hidden');
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls();
    }
}

sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

newChatButton.addEventListener('click', startNewChat);

menuButton.addEventListener('click', () => {
    sidebar.classList.toggle('active');
});

document.addEventListener('DOMContentLoaded', async () => {
    loadingSpinner.style.display = 'none';

    await loadConversations();

    if (initialHistory && initialHistory.length > 0) {
        if (infoMessageBox) infoMessageBox.classList.add('hidden');
        initialHistory.forEach(turn => {
            addMessage(turn.user, 'user');
            addMessage(turn.aeon, 'bot');
        });
        chatControlsContainer.classList.remove('hidden');
        enableControls();
    } else if (currentConversationId && currentConversationId !== 'None') {
        if (infoMessageBox) infoMessageBox.classList.add('hidden');
        addMessage("Hello! I'm Aeon. A personal and local chat bot.", 'bot');
        chatControlsContainer.classList.remove('hidden');
        enableControls();
    }
    else {
        if (infoMessageBox) infoMessageBox.classList.remove('hidden');
        chatControlsContainer.classList.add('hidden');
        disableControls();
    }
});
