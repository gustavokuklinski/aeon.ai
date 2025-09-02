const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const loadingSpinner = document.getElementById('loading-spinner');
const conversationList = document.getElementById('conversation-list');
const newChatButton = document.getElementById('new-chat-button');
const startButton = document.getElementById('start-button');
const chatControlsContainer = document.getElementById('chat-controls-container');
const infoMessageBox = document.getElementById('infoMessageBox'); // Get reference to the static div
const menuButton = document.getElementById('hamburger-menu');
const sidebar = document.querySelector('.sidebar');

const originalMessagePlaceholder = messageInput.placeholder;

// These variables are now retrieved from the HTML file where they were
// processed by the Jinja templating engine.
let currentConversationId = window.currentConversationId;
let initialHistory = window.initialHistory;

// The start button now correctly navigates to the home page
startButton.addEventListener('click', () => { window.location.href = '/'; });

// Function to disable chat controls
function disableControls() {
    messageInput.disabled = true;
    sendButton.disabled = true;
    messageInput.placeholder = "Thinking...";
    // fileInput.disabled = true; // Uncomment if you re-add file input
    // uploadButton.disabled = true; // Uncomment if you re-add file input
}

// Function to enable chat controls
function enableControls() {
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.placeholder = originalMessagePlaceholder;
    messageInput.focus(); // Added this line to automatically focus the input
    // fileInput.disabled = false; // Uncomment if you re-add file input
    // uploadButton.disabled = false; // Uncomment if you re-add file input
}

// Function to create and append a new message div
function addMessage(text, sender) {
    // Hide the info message box if a real message is being added
    if (infoMessageBox && !infoMessageBox.classList.contains('hidden')) {
        infoMessageBox.classList.add('hidden');
    }

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    
    const textSpan = document.createElement('span'); // Create text span
    textSpan.textContent = text;

    if (sender === 'bot') {
        const aeonIcon = document.createElement('img');
        aeonIcon.src = '/assets/img/aeon-icon.png'; // Path to your Aeon icon
        aeonIcon.alt = 'Aeon Icon';
        aeonIcon.classList.add('aeon-message-icon');
        
        // Bot message: Icon then Text
        messageDiv.appendChild(aeonIcon);
        messageDiv.appendChild(textSpan);

    } else if (sender === 'user') {
        // Create a canvas for the user avatar
        const userAvatarCanvas = document.createElement('canvas');
        userAvatarCanvas.classList.add('user-message-avatar');
        // Use currentConversationId as the seed for a consistent avatar per chat
        if (currentConversationId && currentConversationId !== 'None') {
            generateAvatar(userAvatarCanvas, currentConversationId);
        } else {
            // Fallback for initial load or if no conv ID for some reason
            generateAvatar(userAvatarCanvas, "default-user-seed"); 
        }
        
        // User message: Text then Avatar (flex-direction: row-reverse will put avatar on right)
        messageDiv.appendChild(textSpan);
        messageDiv.appendChild(userAvatarCanvas);
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
    
    // Show spinner and disable controls
    loadingSpinner.style.display = 'block';
    chatBox.appendChild(loadingSpinner);
    chatBox.scrollTop = chatBox.scrollHeight;
    disableControls(); // Disable controls while thinking

    try {
        const payload = { message: userMessage };
        // Only send conversation_id if it's a valid string (not "None")
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
        
        loadingSpinner.style.display = 'none'; // Hide spinner
        
        if (response.ok) {
            addMessage(data.response, 'bot');
            // If the backend returns a new conversation_id (meaning a new chat was created),
            // update the frontend's current ID and the browser's URL.
            if (data.conversation_id && data.conversation_id !== currentConversationId) {
                currentConversationId = data.conversation_id;
                window.history.pushState({}, '', `/chat/${currentConversationId}`);
                loadConversations(); // Reload sidebar to highlight new active chat
            }
        } else {
            addMessage(data.response, 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('An error occurred. Please try again.', 'bot');
    } finally {
        // This is the key part: re-enable controls whether the request succeeded or failed
        loadingSpinner.style.display = 'none';
        enableControls(); // Always re-enable controls
    }
}

// Function to handle renaming a conversation
async function renameConversationForweb(convIdToRename, currentName) {
    const newName = await new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'confirm-modal'; // Use the same class as the delete modal
        modal.innerHTML = `
            <div class="confirm-modal-content">
                <p>Current name: <strong>${currentName}</strong></p>
                <input type="text" id="rename-input" placeholder="New Conversation Name" autofocus>
                <div class="confirm-modal-buttons">
                    <button id="rename-update">Update</button>
                    <button id="rename-cancel">Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        const renameInput = document.getElementById('rename-input');
        
        // Live formatting for user input
        renameInput.addEventListener('input', () => {
            let value = renameInput.value;
            value = value.toLowerCase();
            value = value.replaceAll(' ', '-');
            renameInput.value = value;
        });

        document.getElementById('rename-update').onclick = () => {
            let name = renameInput.value.trim();
            name = name.replace(/[^a-z0-9-]/g, '');
            document.body.removeChild(modal);
            resolve(name);
        };
        document.getElementById('rename-cancel').onclick = () => {
            document.body.removeChild(modal);
            resolve(null);
        };
        renameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                let name = renameInput.value.trim();
                name = name.replace(/[^a-z0-9-]/g, '');
                document.body.removeChild(modal);
                resolve(name);
            }
        });
    });

    if (!newName) {
        return; // User cancelled
    }
    
    // Log the ID and new name to the console to help debug
    console.log(`Attempting to rename conversation with ID: "${convIdToRename}" to new name: "${newName}"`);

    loadingSpinner.style.display = 'block';
    disableControls(); // Disable controls during renaming
    try {
        const response = await fetch(`/rename_conversation/${convIdToRename}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName }),
        });

        if (response.ok) {
            // Get the data from the successful response
            const data = await response.json();
            // Update the URL to the new name if this is the currently viewed conversation
            if (currentConversationId === convIdToRename) {
                // The backend now returns the new name as a field in the JSON response
                window.history.pushState({}, '', `/chat/${data.new_name}`);
                currentConversationId = data.new_name; // Update the frontend's internal state
            }
            loadConversations(); // Refresh the list
        } else {
            const data = await response.json();
            const messageBox = document.createElement('div');
            messageBox.className = 'info-message-box';
            // Use the specific error message from the server if available
            const errorMsg = data.message || 'The new name is invalid. Please try a different one.';
            messageBox.textContent = `Error: ${errorMsg}`;
            chatBox.appendChild(messageBox);
            setTimeout(() => chatBox.removeChild(messageBox), 3000); // Remove after 3 seconds
        }
    } catch (error) {
        console.error('Error renaming conversation:', error);
        const messageBox = document.createElement('div');
        messageBox.className = 'info-message-box';
        messageBox.textContent = 'An unexpected network error occurred during renaming. Please check your connection and try again.';
        chatBox.appendChild(messageBox);
        setTimeout(() => chatBox.removeChild(messageBox), 3000); // Remove after 3 seconds
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls(); // Always re-enable controls
    }
}


// Function to fetch and display the list of conversations
async function loadConversations() {
    try {
        const response = await fetch('/conversations');
        const conversations = await response.json();
        
        conversationList.innerHTML = ''; // Clear the list
        if (conversations.length > 0) {
            // Hide the info message box if conversations exist
            if (infoMessageBox) infoMessageBox.classList.add('hidden');

            conversations.forEach(conv => {
                const listItem = document.createElement('li');
                listItem.classList.add('conversation-item'); // Add class for styling
                listItem.setAttribute('data-id', conv.id);

                // Create avatar canvas for the sidebar list item
                const userAvatarCanvas = document.createElement('canvas');
                userAvatarCanvas.classList.add('user-message-avatar');
                generateAvatar(userAvatarCanvas, conv.id); // Use conv.id as seed
                
                // Add click event to the avatar and name
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

                // Create the dropdown menu elements
                const moreOptionsButton = document.createElement('button');
                moreOptionsButton.classList.add('more-options-button');
                moreOptionsButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-ellipsis-vertical"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>`;

                const dropdownMenu = document.createElement('ul');
                dropdownMenu.classList.add('dropdown-menu');
                
                const deleteOption = document.createElement('li');
                deleteOption.classList.add('dropdown-item');
                deleteOption.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M5 20C5 20.5304 5.21071 21.0391 5.58579 21.4142C5.96086 21.7893 6.46957 22 7 22H17C17.5304 22 18.0391 21.7893 18.4142 21.4142C18.7893 21.0391 19 20.5304 19 20V8H5V20ZM16 5H18V7H6V5H8L10 3H14L16 5ZM3 7H21V8H3V7Z"/></svg> Delete`;
                
                const renameOption = document.createElement('li');
                renameOption.classList.add('dropdown-item');
                renameOption.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-i-cursor"><path d="M10 21V3"/><path d="M14 21V3"/></svg> Rename`;

                dropdownMenu.appendChild(renameOption);
                dropdownMenu.appendChild(deleteOption);
                listItem.appendChild(moreOptionsButton);
                listItem.appendChild(dropdownMenu);
                
                // Event listener for the rename option
                renameOption.addEventListener('click', (event) => {
                    event.stopPropagation();
                    renameConversationForweb(conv.id, conv.name); // Pass both ID and NAME
                    dropdownMenu.classList.remove('visible');
                });
                
                // Event listener for the delete option
                deleteOption.addEventListener('click', (event) => {
                    event.stopPropagation(); // Stop event from bubbling up to the list item
                    deleteConversation(conv.id);
                    dropdownMenu.classList.remove('visible'); // Close the menu
                });
                
                // Event listener for the more options button
                moreOptionsButton.addEventListener('click', (event) => {
                    event.stopPropagation(); // Prevent the list item's click from firing
                    // Close any other open menus
                    document.querySelectorAll('.dropdown-menu.visible').forEach(menu => {
                        if (menu !== dropdownMenu) {
                            menu.classList.remove('visible');
                        }
                    });
                    dropdownMenu.classList.toggle('visible');
                });


                if (currentConversationId && currentConversationId !== 'None' && conv.id === currentConversationId) {
                    listItem.classList.add('active');
                }
                conversationList.appendChild(listItem);
            });
            chatControlsContainer.classList.remove('hidden'); // Ensure controls are visible
            enableControls(); // Ensure controls are enabled if conversations exist
        } else {
            // If no conversations, ensure controls are hidden and info message box is visible
            if (infoMessageBox) infoMessageBox.classList.remove('hidden');
            const listItem = document.createElement('li');
            listItem.textContent = 'No conversations found.';
            conversationList.appendChild(listItem);
            chatControlsContainer.classList.add('hidden'); // Ensure controls are hidden here too
            disableControls(); // Disable controls if no conversations
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
        if (infoMessageBox) infoMessageBox.classList.remove('hidden'); // Show info box on error
        const listItem = document.createElement('li');
        listItem.textContent = 'Failed to load conversations.';
        conversationList.appendChild(listItem);
        chatControlsContainer.classList.add('hidden'); // Hide controls on error
        disableControls(); // Disable controls on error
    }
}

// Function to handle deleting a conversation
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
        return; // User cancelled
    }

    loadingSpinner.style.display = 'block';
    disableControls(); // Disable controls during deletion
    try {
        const response = await fetch(`/delete_conversation/${convIdToDelete}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            // If the deleted conversation was the currently active one, redirect to home
            if (currentConversationId === convIdToDelete) {
                currentConversationId = null;
                window.location.href = '/';
            } else {
                loadConversations(); // Refresh the list
            }
        } else {
            const data = await response.json();
            const messageBox = document.createElement('div');
            messageBox.className = 'info-message-box';
            messageBox.textContent = data.message || 'Failed to delete conversation.';
            chatBox.appendChild(messageBox);
            setTimeout(() => chatBox.removeChild(messageBox), 3000); // Remove after 3 seconds
        }
    } catch (error) {
        console.error('Error deleting conversation:', error);
        const messageBox = document.createElement('div');
        messageBox.className = 'info-message-box';
        messageBox.textContent = 'An error occurred during deletion.';
        chatBox.appendChild(messageBox);
        setTimeout(() => chatBox.removeChild(messageBox), 3000); // Remove after 3 seconds
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls(); // Always re-enable controls
    }
}

// Function to handle starting a new chat
async function startNewChat() {
    loadingSpinner.style.display = 'block';
    disableControls(); // Disable controls while starting new chat
    
    try {
        const response = await fetch('/new_chat', { method: 'POST' });
        const data = await response.json();
        
        if (response.ok) {
            window.location.href = `/chat/${data.conversation_id}`;
        } else {
            // Show the error in the chat box, but also ensure info box is hidden if an error occurred in a new chat attempt.
            addMessage(data.message || 'Failed to create new chat.', 'bot');
            if (infoMessageBox) infoMessageBox.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error starting new chat:', error);
        addMessage('An error occurred trying to start a new chat.', 'bot');
        if (infoMessageBox) infoMessageBox.classList.add('hidden');
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls(); // Always re-enable controls
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

// Hamburger menu toggle
menuButton.addEventListener('click', () => {
    sidebar.classList.toggle('active');
});

// Close dropdowns when clicking anywhere on the document
document.addEventListener('click', (event) => {
    document.querySelectorAll('.dropdown-menu.visible').forEach(menu => {
        if (!menu.contains(event.target) && !menu.previousElementSibling.contains(event.target)) {
            menu.classList.remove('visible');
        }
    });
});

// Load conversation on page load
document.addEventListener('DOMContentLoaded', async () => { // Changed to async
    loadingSpinner.style.display = 'none'; // Ensure spinner is hidden initially

    // First, load conversations to determine if any exist
    await loadConversations(); // Wait for conversations to load

    if (initialHistory && initialHistory.length > 0) {
        if (infoMessageBox) infoMessageBox.classList.add('hidden'); // Hide info box if history exists
        initialHistory.forEach(turn => {
            addMessage(turn.user, 'user');
            addMessage(turn.aeon, 'bot');
        });
        chatControlsContainer.classList.remove('hidden'); // Ensure controls are visible if history exists
        enableControls(); // Enable controls if history exists
    } else if (currentConversationId && currentConversationId !== 'None') {
        if (infoMessageBox) infoMessageBox.classList.add('hidden'); // Hide info box if a new empty chat
        addMessage("Hello! I'm Aeon. A personal and local chat bot.", 'bot');
        chatControlsContainer.classList.remove('hidden'); // Ensure controls are visible for a new, empty chat
        enableControls(); // Enable controls for a new, empty chat
    }
    else {
        // If no initial history and no current conversation ID, display the info message box
        if (infoMessageBox) infoMessageBox.classList.remove('hidden'); // Ensure info box is visible
        chatControlsContainer.classList.add('hidden'); // Explicitly hide controls here if no conversations
        disableControls(); // Disable controls if no conversations
    }
});
