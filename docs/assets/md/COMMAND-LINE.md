# Command line

Commands can be placed directly in the terminal chat interface:

* `/help`: Show list of commands.
* `/new`: Create a new conversation.
* `/list`: List all conversations.
* `/open <NUMBER>`: Open a conversation.
* `/load <NUMBER>`: Ingest a previous conversation.
* `/ingest <PATH> | <PATH><filename.json,txt,md>`: Add documents to RAG.
* `/zip`: Backup contents to a timestamped zip file.
* `/search <TERM>`: Make a web search with DuckDuckGo.
* `/quit`, `/exit`, `/bye`: End the conversation.


## Plugins (Build-in)

* `/hello <PROMPT>`: Simple Hello World plugin
* `/image <PROMPT>`: Generate an image. Model: [segmind/tiny-sd](https://huggingface.co/segmind/tiny-sd)
* `/view <PATH><filename.png, jpg> <PROMPT>`: Visualize an image. Model: [HuggingFaceTB/SmolVLM-256M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct)