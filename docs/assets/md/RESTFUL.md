# **AEON API Routes**

This document outlines the API endpoints for the AEON web application. All endpoints are based on a RESTful design and handle conversation management, RAG (Retrieval-Augmented Generation) chat, and backup functionality.

### **/**

**GET**  
Description: Renders the main chat interface HTML page. This is the entry point for the application.  
Request: None  
Response: Renders index.html.

### **/chat/\<string:conv\_id\>**

**GET**  
Description: Renders the chat interface for a specific conversation ID. If the conversation history exists, it is loaded and displayed.  
Request:

* URL Parameter: conv\_id (string) \- The unique ID of the conversation to load.  
  Response: Renders index.html with the specified conversation history.

### **/new\_chat**

**POST**  
Description: Creates a new conversation, generates a unique conversation ID, and redirects the user to the new chat page.  
Request: None  
Response:

* **Status Code:** 200 OK  
* **JSON Body:**  
  {  
    "conversation\_id": "string",  
    "redirect\_url": "string"  
  }

* **Error Response:**  
  * **Status Code:** 500 Internal Server Error  
  * **JSON Body:** {"message": "string"}

### **/chat**

**POST**  
Description: Processes a user's message using the RAG system and returns a response from the AI. If no conversation\_id is provided, a new conversation is created.  
Request:

* **JSON Body:**  
  {  
    "message": "string",  
    "conversation\_id": "string"  
  }

**Response:**

* **Status Code:** 200 OK  
* **JSON Body:**  
  {  
    "response": "string",  
    "conversation\_id": "string"  
  }

* **Error Response:**  
  * **Status Code:** 400 Bad Request if no message is provided.  
  * **Status Code:** 500 Internal Server Error if an error occurs during RAG processing.  
  * **JSON Body:** {"response": "string"}

### **/conversations**

**GET**  
Description: Lists all available conversations by scanning the memory directory.  
Request: None  
Response:

* **Status Code:** 200 OK  
* **JSON Body:** An array of objects, where each object represents a conversation.  
  \[  
    {"id": "string", "name": "string"},  
    ...  
  \]

### **/conversation/\<string:conv\_id\>**

**GET**  
Description: Retrieves the complete history of a specific conversation.  
Request:

* URL Parameter: conv\_id (string) \- The unique ID of the conversation.  
  Response:  
* **Status Code:** 200 OK  
* **JSON Body:** An array of message objects representing the conversation history.  
  \[  
    {"user": "string", "aeon": "string"},  
    ...  
  \]

* **Error Response:**  
  * **Status Code:** 404 Not Found if the conversation ID is not found.  
  * **Status Code:** 500 Internal Server Error if an error occurs while loading the history.  
  * **JSON Body:** {"message": "string"}

### **/delete\_conversation/\<string:conv\_id\>**

**DELETE**  
Description: Deletes a conversation and all its contents from the server.  
Request:

* URL Parameter: conv\_id (string) \- The unique ID of the conversation to delete.  
  Response:  
* **Status Code:** 200 OK  
* **JSON Body:** {"message": "Conversation deleted successfully."}  
* **Error Response:**  
  * **Status Code:** 404 Not Found if the conversation ID is not found.  
  * **Status Code:** 500 Internal Server Error if deletion fails.  
  * **JSON Body:** {"message": "string"}

### **/rename\_conversation/\<string:conv\_id\>**

**PATCH**  
Description: Renames a conversation by its ID.  
Request:

* **URL Parameter:** conv\_id (string) \- The unique ID of the conversation to rename.  
* JSON Body: {"name": "string"} \- The new name for the conversation.  
  Response:  
* **Status Code:** 200 OK  
* **JSON Body:** {"message": "Conversation renamed successfully.", "new\_name": "string"}  
* **Error Response:**  
  * **Status Code:** 400 Bad Request if the ID or new name is missing.  
  * **Status Code:** 500 Internal Server Error if renaming fails.  
  * **JSON Body:** {"message": "string"}

### **/load\_backup**

**POST**  
Description: Uploads and loads a conversation backup from a .zip file.  
Request:

* Form Data: file (a .zip file containing the backup).  
  Response:  
* **Status Code:** 200 OK  
* **JSON Body:**  
  {  
    "message": "Backup loaded successfully.",  
    "redirect\_url": "string"  
  }

* **Error Response:**  
  * **Status Code:** 400 Bad Request if no file is provided or the file type is invalid.  
  * **Status Code:** 500 Internal Server Error if the backup fails to load.  
  * **JSON Body:** {"message": "string"}

### **/zip\_backup/\<string:conv\_id\>**

**GET**  
Description: Creates a zip file of a conversation's memory folder for backup.  
Request:

* URL Parameter: conv\_id (string) \- The unique ID of the conversation to back up.  
  Response:  
* **Status Code:** 200 OK  
* **JSON Body:**  
  {  
    "message": "Backup created.",  
    "zip\_file": "string"  
  }

* **Error Response:**  
  * **Status Code:** 404 Not Found if the conversation ID is not found.  
  * **Status Code:** 500 Internal Server Error if zipping fails.  
  * **JSON Body:** {"message": "string"}

### **/download\_backup/\<path:filename\>**

**GET**  
Description: Serves the created backup zip file for download and then deletes it from the server.  
Request:

* URL Parameter: filename (string) \- The name of the zip file to download.  
  Response: A downloadable file.  
* **Error Response:**  
  * **Status Code:** 404 Not Found if the file doesn't exist.  
  * **Status Code:** 500 Internal Server Error if an error occurs.  
  * **Plain Text:** "An error occurred during download."

### **/serve\_from\_memory/\<folder\>/\<path:filename\>**

**GET**  
Description: Serves a static file from a specific subfolder within a conversation's memory directory.  
Request:

* **URL Parameters:**  
  * folder (string) \- The subfolder name (e.g., docs).  
  * filename (string) \- The name of the file to serve.  
* Query Parameter: conv\_id (string) \- The ID of the conversation.  
  Response: The requested file.  
* **Error Response:**  
  * **Status Code:** 404 Not Found if the file or folder is not found.  
  * **Plain Text:** "File not found."

### **/api/config/\<conv\_id\>**

**GET**  
Description: Retrieves the content of the config.yml file for a specified conversation.  
Request:

* URL Parameter: conv\_id (string) \- The ID of the conversation.  
  Response:  
* **Status Code:** 200 OK  
* **JSON Body:** {"config\_content": "string"} \- The YAML content as a string.  
* **Error Response:**  
  * **Status Code:** 404 Not Found if the config file is not found.  
  * **Status Code:** 500 Internal Server Error if an error occurs while reading the file.  
  * **JSON Body:** {"message": "string"}

### **/api/config/\<conv\_id\>**

**POST**  
Description: Saves new content to the config.yml file for a specified conversation. The content is validated as YAML before saving.  
Request:

* **URL Parameter:** conv\_id (string) \- The ID of the conversation.  
* JSON Body: {"config\_content": "string"} \- The new YAML content as a string.  
  Response:  
* **Status Code:** 200 OK  
* **JSON Body:** {"message": "Configuration saved successfully."}  
* **Error Response:**  
  * **Status Code:** 400 Bad Request if no content is provided or the content is invalid YAML.  
  * **Status Code:** 500 Internal Server Error if saving the file fails.  
  * **JSON Body:** {"message": "string"}