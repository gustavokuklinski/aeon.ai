const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const loadingSpinner = document.getElementById('loading-spinner');
const conversationList = document.getElementById('conversation-list');
const newChatButton = document.getElementById('new-chat-button');
const chatControlsContainer = document.getElementById('chat-controls-container');

// Function to create and append a new message div
function addMessage(text, sender, imageUrl = null) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    // Add the text content
    messageDiv.textContent = text;
    
    // If an image URL is provided, create and append an img element
    if (imageUrl) {
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = 'Generated Image';
        messageDiv.appendChild(img);
    }
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
}

// Function to handle sending a message
async function sendMessage() {
    const userMessage = messageInput.value.trim();
    if (userMessage === '') return;

    addMessage(userMessage, 'user');
    messageInput.value = '';
    loadingSpinner.style.display = 'block'; // Show spinner

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage, conversation_id: currentConversationId }),
        });

        const data = await response.json();
        
        loadingSpinner.style.display = 'none'; // Hide spinner
        
        if (response.ok) {
            if (data.image_url) {
                addMessage(data.response, 'bot', data.image_url);
            } else {
                addMessage(data.response, 'bot');
            }
        } else {
            addMessage(data.response, 'bot');
        }
    } catch (error) {
        loadingSpinner.style.display = 'none'; // Hide spinner
        console.error('Error:', error);
        addMessage('An error occurred. Please try again.', 'bot');
    }
}


// Function to fetch and display the list of conversations
async function loadConversations() {
    try {
        const response = await fetch('/conversations');
        const conversations = await response.json();
        
        conversationList.innerHTML = ''; // Clear the list
        if (conversations.length > 0) {
            chatControlsContainer.classList.remove('hidden');
            conversations.forEach(conv => {
                const listItem = document.createElement('li');
                listItem.textContent = conv.name;
                listItem.setAttribute('data-id', conv.id);
                if (currentConversationId && conv.id === currentConversationId) {
                    listItem.classList.add('active');
                }
                listItem.addEventListener('click', () => {
                    // Redirect to the URL for this conversation
                    window.location.href = `/chat/${conv.id}`;
                });
                conversationList.appendChild(listItem);
            });
        } else {
            const listItem = document.createElement('li');
            listItem.textContent = 'No conversations found.';
            conversationList.appendChild(listItem);
            chatControlsContainer.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
        const listItem = document.createElement('li');
        listItem.textContent = 'Failed to load conversations.';
        conversationList.appendChild(listItem);
        chatControlsContainer.classList.add('hidden');
    }
}

// Function to handle starting a new chat
async function startNewChat() {
    loadingSpinner.style.display = 'block';
    
    try {
        const response = await fetch('/new_chat', { method: 'POST' });
        const data = await response.json();
        
        if (response.ok) {
            // Redirect to the URL for the new chat
            window.location.href = `/chat/${data.conversation_id}`;
        } else {
            addMessage(data.message || 'Failed to create new chat.', 'bot');
        }
    } catch (error) {
        console.error('Error starting new chat:', error);
        addMessage('An error occurred trying to start a new chat.', 'bot');
    } finally {
        loadingSpinner.style.display = 'none';
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

newChatButton.addEventListener('click', startNewChat);

// Load conversation on page load
document.addEventListener('DOMContentLoaded', () => {
    if (initialHistory.length > 0) {
        initialHistory.forEach(turn => {
            addMessage(turn.user, 'user');
            addMessage(turn.aeon, 'bot');
        });
    } else {
        startNewChat()
    }
});
