// web/assets/js/chat.js
document.getElementById('chat-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const userInput = document.getElementById('user-input').value;
    if (!userInput) return;

    const chatWindow = document.getElementById('chat-window');

    // Display user message
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user';
    userMessageDiv.innerHTML = `<p><strong>[USER] </strong> ${userInput}</p>`;
    chatWindow.appendChild(userMessageDiv);

    // Clear input field
    document.getElementById('user-input').value = '';

    // Display a loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message system loading';
    loadingDiv.innerHTML = `<p><strong>[AEON] </strong> Thinking...</p>`;
    chatWindow.appendChild(loadingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Send request to Flask backend
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        chatWindow.removeChild(loadingDiv);
        
        // Display AEON's response
        const aeonMessageDiv = document.createElement('div');
        aeonMessageDiv.className = 'message system';

        // Check for an image URL and display an image if present
        if (data.image_url) {
            aeonMessageDiv.innerHTML = `
                <p><strong>[AEON] </strong> ${data.response}</p>
                <img src="${data.image_url}" alt="${userInput.replace('/image', '').trim()}" style="max-width: 100%; border-radius: 8px; margin-top: 10px;">
            `;
        } else {
            // Display text response as before
            aeonMessageDiv.innerHTML = `<p><strong>[AEON] </strong> ${data.response}</p>`;
        }

        chatWindow.appendChild(aeonMessageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
        // Remove loading indicator
        chatWindow.removeChild(loadingDiv);
        
        // Display error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message system error';
        errorDiv.innerHTML = `<p><strong>[AEON] </strong> An error occurred. Please try again.</p>`;
        chatWindow.appendChild(errorDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    });
});


// New code for file ingestion
document.getElementById('ingest-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const fileInput = document.getElementById('ingest-file');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file to ingest.");
        return;
    }

    const chatWindow = document.getElementById('chat-window');

    // Display AEON's thinking message
    const thinkingMessageDiv = document.createElement('div');
    thinkingMessageDiv.className = 'message system loading';
    thinkingMessageDiv.innerHTML = `<p><strong>[AEON] </strong> Ingesting file: <strong>${file.name}</strong>...</p>`;
    chatWindow.appendChild(thinkingMessageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload_and_ingest', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        // Remove the loading message
        chatWindow.removeChild(thinkingMessageDiv);

        // Display the AEON's response
        const aeonMessageDiv = document.createElement('div');
        aeonMessageDiv.className = 'message system';
        aeonMessageDiv.innerHTML = `<p><strong>[AEON] </strong> ${data.message}</p>`;
        chatWindow.appendChild(aeonMessageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        // Clear the file input
        fileInput.value = '';
    })
    .catch(error => {
        console.error('Error during file ingestion:', error);
        chatWindow.removeChild(thinkingMessageDiv);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message system error';
        errorDiv.innerHTML = `<p><strong>[AEON] </strong> Failed to ingest file. Check the console for details.</p>`;
        chatWindow.appendChild(errorDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    });
});