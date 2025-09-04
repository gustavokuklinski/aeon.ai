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
const uploadBackupButton = document.getElementById('upload-backup-button');
const configButton = document.getElementById('config-button');
const configModal = document.getElementById('config-modal');
const configTextarea = document.getElementById('config-textarea');
const configSaveButton = document.getElementById('config-save-button');
const configCancelButton = document.getElementById('config-cancel-button');
const commandList = document.getElementById('command-list');
const ingestButton = document.getElementById('ingest-button');

const originalMessagePlaceholder = messageInput.placeholder;

// These variables are now retrieved from the HTML file where they were
// processed by the Jinja templating engine.
let currentConversationId = window.currentConversationId;
let initialHistory = window.initialHistory;

// The start button now correctly navigates to the home page
startButton.addEventListener('click', () => { window.location.href = '/'; });

const availableCommands = [
    { cmd: '/new', desc: 'Create a new chat.' },
    { cmd: '/open [CHAT_ID]', desc: 'Open a chat by number.' },
    { cmd: '/zip', desc: 'Backup contents to a zip file at /data/output/backup' },
    { cmd: '/ingest', desc: 'Add documents to RAG. Accept only: txt, md and json' },
    { cmd: '/load', desc: 'Load a ZIP backup.' },
    { cmd: '/search [TERM]', desc: 'Make a web search by term and /ingest' },
    { cmd: '/rename [OLD_CHAT_ID] [NEW_CHAT_ID]', desc: 'Rename a chat by ID.' },
    { cmd: '/delete [CHAT_ID]', desc: 'Delete a selected chat.' },
];

/**
 * Disables chat controls (input, send button) and shows a loading state.
 */
function disableControls() {
    messageInput.disabled = true;
    sendButton.disabled = true;
    messageInput.placeholder = "Thinking...";
    ingestButton.disabled = true;
}

/**
 * Enables chat controls and focuses the message input.
 */
function enableControls() {
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.placeholder = originalMessagePlaceholder;
    messageInput.focus();
    ingestButton.disabled = false;
}

/**
 * Creates and appends a new message div to the chat box.
 * @param {string} text - The message content.
 * @param {string} sender - 'user' or 'bot'.
 */
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

        const botTextContent = document.createElement('div');
        botTextContent.innerHTML = marked.parse(text);

        messageDiv.appendChild(aeonIcon);
        messageDiv.appendChild(botTextContent);
    } else if (sender === 'user') {
        const userAvatarCanvas = document.createElement('canvas');
        userAvatarCanvas.classList.add('user-message-avatar');
        // NOTE: The `generateAvatar` function is a dependency not included in this file.
        // It must be defined elsewhere for this to work.
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

/**
 * Handles sending a message to the backend API.
 */
async function sendMessage() {
    const userMessage = messageInput.value.trim();
    if (userMessage === '') return;

    const [command, ...args] = userMessage.split(' ');
    const fullCommand = command.toLowerCase();

    switch (fullCommand) {
        case '/new':
            startNewChat();
            return;
        case '/open':
            const chatId = args[0];
            if (chatId) {
                window.location.href = `/chat/${chatId}`;
            } else {
                addMessage('Please provide a valid chat ID. Example: /open my-chat-id', 'bot');
            }
            return;
        case '/zip':
            if (currentConversationId && currentConversationId !== 'None') {
                zipConversation(currentConversationId);
            } else {
                addMessage('Please select a conversation to back up.', 'bot');
            }
            return;
        case '/delete':
            const idToDelete = args[0];
            if (idToDelete) {
                deleteConversation(idToDelete);
            } else {
                addMessage('Please provide a chat ID to delete. Example: /delete my-old-chat', 'bot');
            }
            return;
        case '/load':
            uploadBackupButton.click(); // Triggers the file selection dialog
            return;
        case '/search':
            const searchTerm = args.join(' ');
            if (searchTerm) {
                webSearch(searchTerm);
            } else {
                showInfoMessage('Please provide a search term. Example: /search latest tech news', 'bot');
            }
            return;
        case '/ingest':
            ingestButton.click(); // Triggers the file selection dialog for ingestion
            return;
        default:
            // Continue with normal message sending
            break;
    }

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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

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

/**
 * Reusable function to create a modal with a custom message and buttons.
 * @param {string} contentHtml - The HTML content for the modal.
 * @returns {Promise<boolean|string|null>} A promise that resolves with the result of the user's action.
 */
function createModal(contentHtml) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'confirm-modal';
        modal.innerHTML = `<div class="confirm-modal-content">${contentHtml}</div>`;
        document.body.appendChild(modal);

        // Function to handle cleanup and resolution
        const cleanup = (result) => {
            document.body.removeChild(modal);
            resolve(result);
        };

        const yesButton = document.getElementById('confirm-yes');
        const noButton = document.getElementById('confirm-no');
        const updateButton = document.getElementById('rename-update');
        const cancelButton = document.getElementById('rename-cancel');
        const renameInput = document.getElementById('rename-input');

        if (yesButton) yesButton.onclick = () => cleanup(true);
        if (noButton) noButton.onclick = () => cleanup(false);

        if (updateButton && renameInput) {
            renameInput.addEventListener('input', () => {
                let value = renameInput.value.toLowerCase().replaceAll(' ', '-');
                renameInput.value = value;
            });
            updateButton.onclick = () => {
                let name = renameInput.value.trim().replace(/[^a-z0-9-]/g, '');
                cleanup(name);
            };
            cancelButton.onclick = () => cleanup(null);
            renameInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    let name = renameInput.value.trim().replace(/[^a-z0-9-]/g, '');
                    cleanup(name);
                }
            });
        }
    });
}

async function webSearch(searchTerm) {
    if (!currentConversationId || currentConversationId === 'None') {
        showInfoMessage("Please start or select a conversation first.");
        return;
    }

    addMessage(`Searching the web for: "${searchTerm}"...`, 'user');
    messageInput.value = '';
    loadingSpinner.style.display = 'block';
    disableControls();

    try {
        const payload = {
            search_term: searchTerm,
            conversation_id: currentConversationId
        };

        const response = await fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (typeof data.response === 'string' && data.response.includes('\n\nTitle:')) {
            const [summary, ...linkBlocks] = data.response.split('\n\nTitle:');

            let formattedLinks = '';
            linkBlocks.forEach(block => {
                const lines = block.split('\n');
                if (lines.length >= 2) {
                    const title = lines[0].trim();
                    const linkUrl = lines[1].replace('Link:', '').trim();
                    formattedLinks += `<br /><br />Title: ${title}<br />Link: <a href="${linkUrl}" class="search-result-link" target="_blank">${linkUrl}</a>`;
                }
            });
            const finalMessage = `${summary.trim()}${formattedLinks}`;
            addMessage(finalMessage, 'bot');
        } else {
            addMessage(data.response, 'bot');
        }

    } catch (error) {
        console.error('Error during web search:', error);
        showInfoMessage('An unexpected network error occurred. Please try again.');
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls();
    }
}

/**
 * Handles renaming a conversation via a modal prompt.
 * @param {string} convIdToRename - The ID of the conversation to rename.
 * @param {string} currentName - The current name of the conversation.
 */
async function renameConversationForweb(convIdToRename, currentName) {
    const newName = await createModal(`
        <p>Current name: <strong>${currentName}</strong></p>
        <input type="text" id="rename-input" placeholder="New Conversation Name" autofocus>
        <div class="confirm-modal-buttons">
            <button id="rename-update">Update</button>
            <button id="rename-cancel">Cancel</button>
        </div>
    `);

    if (!newName) {
        return;
    }

    console.log(`Attempting to rename conversation with ID: "${convIdToRename}" to new name: "${newName}"`);

    loadingSpinner.style.display = 'block';
    disableControls();
    try {
        const response = await fetch(`/rename_conversation/${convIdToRename}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName }),
        });

        if (response.ok) {
            const data = await response.json();
            if (currentConversationId === convIdToRename) {
                window.history.pushState({}, '', `/chat/${data.new_name}`);
                currentConversationId = data.new_name;
            }
            loadConversations();
        } else {
            const data = await response.json();
            showInfoMessage(data.message || 'The new name is invalid. Please try a different one.');
        }
    } catch (error) {
        console.error('Error renaming conversation:', error);
        showInfoMessage('An unexpected network error occurred during renaming. Please check your connection and try again.');
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls();
    }
}

/**
 * Shows a temporary info message in the chat box.
 * @param {string} message - The message to display.
 */
function showInfoMessage(message) {
    const messageBox = document.createElement('div');
    messageBox.className = 'info-message-box';
    messageBox.textContent = message;
    chatBox.appendChild(messageBox);
    setTimeout(() => chatBox.removeChild(messageBox), 3000);
}

/**
 * Zips a conversation for backup.
 * @param {string} convId - The ID of the conversation to zip.
 */
function zipConversation(convId) {
    showInfoMessage('Creating backup. Please wait...');
    fetch(`/zip_backup/${convId}`)
        .then(response => response.json())
        .then(data => {
            if (data.zip_file) {
                const downloadUrl = `/download_backup/${data.zip_file}`;
                const messageBox = document.createElement('div');
                messageBox.className = 'info-message-box';
                messageBox.innerHTML = `Backup created successfully. <a href="${downloadUrl}" class="download-backup" download>Click to download.</a>`;
                chatBox.appendChild(messageBox);
            } else {
                showInfoMessage(data.message || 'Failed to create backup.');
            }
        })
        .catch(error => {
            console.error('Error creating backup:', error);
            showInfoMessage('An error occurred while creating the backup.');
        });
}

/**
 * Fetches and displays the list of conversations in the sidebar.
 */
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
                renameOption.innerHTML = `<svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="rename"><path d="M12.9167 4.25L13.75 3.41667C13.9242 3.24242 14.1614 3.14152 14.4093 3.14152C14.6572 3.14152 14.8944 3.24242 15.0687 3.41667C15.2429 3.59091 15.3438 3.82806 15.3438 4.07598C15.3438 4.32391 15.2429 4.56106 15.0687 4.7353L14.2353 5.56863C14.0725 5.73147 13.9112 5.88582 13.75 6.04167L12.9167 5.20833C13.0805 5.04453 13.2353 4.88331 13.3917 4.7353L12.9167 4.25ZM11.4167 5.75L12.25 6.58333L6.33333 12.5L5.5 13.3333L4.66667 12.5L3.83333 11.6667L10.5833 4.91667L11.4167 5.75ZM3.83333 14.1667C3.5971 14.1667 3.36086 14.2676 3.18662 14.4418C3.01237 14.6161 2.91147 14.8523 2.91147 15.1011V15.9333H16.1667V15.1011C16.1667 14.8649 16.0658 14.6286 15.8916 14.4544C15.7173 14.2801 15.4811 14.1792 15.2449 14.1792L3.83333 14.1667Z" fill="white"/></g></svg> Rename`;

                const zipItem = document.createElement('li');
                zipItem.classList.add('dropdown-item');
                zipItem.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-archive"><rect width="20" height="5" x="2" y="3" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/><path d="M10 12h4"/></svg> Zip Backup`;
                zipItem.onclick = (e) => {
                    e.stopPropagation();
                    dropdownMenu.classList.remove('visible');
                    zipConversation(conv.id);
                };

                dropdownMenu.appendChild(renameOption);
                dropdownMenu.appendChild(zipItem);
                dropdownMenu.appendChild(deleteOption);
                listItem.appendChild(moreOptionsButton);
                listItem.appendChild(dropdownMenu);

                renameOption.addEventListener('click', (event) => {
                    event.stopPropagation();
                    renameConversationForweb(conv.id, conv.name);
                    dropdownMenu.classList.remove('visible');
                });

                deleteOption.addEventListener('click', (event) => {
                    event.stopPropagation();
                    deleteConversation(conv.id);
                    dropdownMenu.classList.remove('visible');
                });

                moreOptionsButton.addEventListener('click', (event) => {
                    event.stopPropagation();
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

/**
 * Handles deleting a conversation after a user confirmation.
 * @param {string} convIdToDelete - The ID of the conversation to delete.
 */
async function deleteConversation(convIdToDelete) {
    const userConfirmed = await createModal(`
        <p>Are you sure you want to delete this conversation? This action cannot be undone.</p>
        <div class="confirm-modal-buttons">
            <button id="confirm-yes">Yes</button>
            <button id="confirm-no">No</button>
        </div>
    `);

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
            showInfoMessage(data.message || 'Failed to delete conversation.');
        }
    } catch (error) {
        console.error('Error deleting conversation:', error);
        showInfoMessage('An error occurred during deletion.');
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls();
    }
}

/**
 * Handles starting a new chat session.
 */
async function startNewChat() {
    loadingSpinner.style.display = 'block';
    disableControls();

    try {
        const response = await fetch('/new_chat', { method: 'POST' });
        const data = await response.json();

        if (response.ok) {
            window.location.href = `/chat/${data.conversation_id}`;
        } else {
            showInfoMessage(data.message || 'Failed to create new chat.', 'bot');
            if (infoMessageBox) infoMessageBox.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error starting new chat:', error);
        showInfoMessage('An error occurred trying to start a new chat.', 'bot');
        if (infoMessageBox) infoMessageBox.classList.add('hidden');
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls();
    }
}

/**
 * Handles uploading a backup file.
 * @param {File} file - The selected file object.
 */
async function uploadBackup(file) {
    if (!file) {
        return;
    }

    loadingSpinner.style.display = 'block';
    disableControls();

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/load_backup', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            addMessage(data.message, 'bot');
            loadConversations();
        } else {
            addMessage(data.message, 'bot');
        }
    } catch (error) {
        console.error('Error uploading backup:', error);
        addMessage('An error occurred during the backup upload. Please try again.', 'bot');
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls();
    }
}

/**
 * Handles file ingestion via upload.
 * @param {File} file - The file to be ingested.
 */
async function ingestFile(file) {
    if (!file) {
        return;
    }

    if (!currentConversationId || currentConversationId === 'None') {
        showInfoMessage("Please start or select a conversation first.");
        return;
    }

    showInfoMessage(`Ingesting file: ${file.name}...`);
    disableControls();

    const formData = new FormData();
    formData.append('file', file);
    formData.append('conversation_id', currentConversationId);

    try {
        const response = await fetch('/ingest', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            showInfoMessage(data.message);
        } else {
            showInfoMessage(data.message);
        }
    } catch (error) {
        console.error('Error ingesting file:', error);
        showInfoMessage('An error occurred during file ingestion. Please try again.', 'bot');
    } finally {
        loadingSpinner.style.display = 'none';
        enableControls();
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

uploadBackupButton.addEventListener('click', () => {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.zip';
    fileInput.style.display = 'none';

    fileInput.addEventListener('change', (event) => {
        const selectedFile = event.target.files[0];
        if (selectedFile) {
            uploadBackup(selectedFile);
        }
    });

    document.body.appendChild(fileInput);
    fileInput.click();
    document.body.removeChild(fileInput);
});

ingestButton.addEventListener('click', () => {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.md,.txt,.json';
    fileInput.style.display = 'none';

    fileInput.addEventListener('change', (event) => {
        const selectedFile = event.target.files[0];
        if (selectedFile) {
            ingestFile(selectedFile);
        }
    });

    document.body.appendChild(fileInput);
    fileInput.click();
    document.body.removeChild(fileInput);
});

configButton.addEventListener('click', async () => {
    if (!currentConversationId || currentConversationId === 'None') {
        showInfoMessage("Please start or select a conversation first.");
        return;
    }

    // Show the modal and a temporary loading message
    const configHtml = `
        <p><strong>Configuration for ${currentConversationId}</strong></p>
        <textarea id="config-textarea" class="config-textarea" rows="20" cols="50" placeholder="Loading..." wrap='off'></textarea>
        <p>When [SAVE] Chat will be reloaded</p>
        <div class="confirm-modal-buttons">
            <button id="config-save-button">Save</button>
            <button id="config-cancel-button">Cancel</button>
        </div>
    `;

    // Use createModal to create a temporary modal and get the element for a brief moment
    const tempModal = document.createElement('div');
    tempModal.className = 'confirm-modal';
    tempModal.innerHTML = `<div class="confirm-modal-content">${configHtml}</div>`;
    document.body.appendChild(tempModal);

    const configTextArea = tempModal.querySelector('#config-textarea');
    const saveButton = tempModal.querySelector('#config-save-button');
    const cancelButton = tempModal.querySelector('#config-cancel-button');

    // Add event listeners within the context of the newly created modal
    saveButton.addEventListener('click', async () => {
        const newConfig = configTextArea.value;
        disableControls();

        try {
            const response = await fetch(`/api/config/${currentConversationId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ config_content: newConfig })
            });
            const data = await response.json();
            if (response.ok) {
                showInfoMessage(data.message);
                window.location.href = '/';
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Error saving config:', error);
            showInfoMessage(`Failed to save config: ${error.message}`);
        } finally {
            enableControls();
            document.body.removeChild(tempModal);
        }
    });

    cancelButton.addEventListener('click', () => {
        document.body.removeChild(tempModal);
    });

    // Fetch and display config
    disableControls();
    try {
        const response = await fetch(`/api/config/${currentConversationId}`);
        const data = await response.json();
        if (response.ok) {
            configTextArea.value = data.config_content;
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error fetching config:', error);
        configTextArea.value = `Error loading config: ${error.message}`;
    } finally {
        enableControls();
    }
});


// Hamburger menu toggle
menuButton.addEventListener('click', () => {
    sidebar.classList.toggle('active');
});

// Close dropdowns when clicking anywhere on the document
document.addEventListener('click', (event) => {
    document.querySelectorAll('.dropdown-menu.visible').forEach(menu => {
        const moreOptionsButton = menu.previousElementSibling;
        if (!menu.contains(event.target) && !moreOptionsButton.contains(event.target)) {
            menu.classList.remove('visible');
        }
    });
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
    } else {
        if (infoMessageBox) infoMessageBox.classList.remove('hidden');
        chatControlsContainer.classList.add('hidden');
        disableControls();
    }
});

messageInput.addEventListener('input', () => {
    const value = messageInput.value.trim();
    if (value.startsWith('/')) {
        const searchTerm = value.substring(1).toLowerCase();
        const filteredCommands = availableCommands.filter(command => command.cmd.toLowerCase().includes(searchTerm));
        displayCommands(filteredCommands);
        commandList.classList.remove('hidden');
    } else {
        commandList.classList.add('hidden');
    }
});

function displayCommands(commands) {
    commandList.innerHTML = '';
    if (commands.length === 0) {
        commandList.classList.add('hidden');
        return;
    }

    commands.forEach(command => {
        const commandItem = document.createElement('div');
        commandItem.classList.add('command-list-item');
        commandItem.innerHTML = `<strong>${command.cmd}</strong> - ${command.desc}`;
        commandItem.addEventListener('click', () => {
            messageInput.value = `${command.cmd} `;
            commandList.classList.add('hidden');
            messageInput.focus();
        });
        commandList.appendChild(commandItem);
    });
}