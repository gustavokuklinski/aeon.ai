document.getElementById('chat-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const userInput = document.getElementById('user-input').value;
            if (!userInput) return;

            const chatWindow = document.getElementById('chat-window');

            // Display user message
            const userMessageDiv = document.createElement('div');
            userMessageDiv.className = 'message user';
            userMessageDiv.innerHTML = `<p><strong>[>>>>] </strong> ${userInput}</p>`;
            chatWindow.appendChild(userMessageDiv);

            // Clear input field
            document.getElementById('user-input').value = '';

            // Display a loading indicator
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message system loading';
            loadingDiv.innerHTML = `<p><strong>[AEON] </strong> Thinking...</p>`;
            chatWindow.appendChild(loadingDiv);
            chatWindow.scrollTop = chatWindow.scrollHeight;

            // Send to Flask API
            fetch('/api/chat', {
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

                // Display AI response
                const aiMessageDiv = document.createElement('div');
                aiMessageDiv.className = 'message system';
                aiMessageDiv.innerHTML = `<p><strong>[AEON] </strong> ${data.response || data.error}</p>`;
                chatWindow.appendChild(aiMessageDiv);

                // Scroll to the bottom
                chatWindow.scrollTop = chatWindow.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
                chatWindow.removeChild(loadingDiv);
                const errorDiv = document.createElement('div');
                errorDiv.className = 'message system error';
                errorDiv.innerHTML = `<p><strong>[AEON] </strong> An error occurred. Please try again.</p>`;
                chatWindow.appendChild(errorDiv);
                chatWindow.scrollTop = chatWindow.scrollHeight;
            });
        });