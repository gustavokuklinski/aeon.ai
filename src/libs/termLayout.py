from src.config import (
    LLM_MODEL,
    EMB_MODEL,
    LOADED_PLUGINS
)
from src.libs.messages import print_command_message, print_info_message, print_error_message
from src.libs.plugins import PluginManager

def printAeonLayout():
    print("\033[38;5;160m_______________________________________________________\033[0m")
    print("")
    print("\033[38;5;160m      ###       #########      ######     ###      ### \033[0m")
    print("\033[38;5;160m    ### ###     ##          ###      ###  ######   ### \033[0m")
    print("\033[38;5;160m   ###   ###    #########  ###       ###  ###  ### ### \033[0m")
    print("\033[38;5;160m  ###     ###   ##          ##       ###  ###   ###### \033[0m")
    print("\033[38;5;160m ##         ##  #########     #######     ###      ### \033[0m")
    print("\033[38;5;160m_______________________________________________________\033[0m")
    print("")


def printAeonCmd():
    print("Commands to use:")
    print_command_message("'/help' Show this screen.")
    print_command_message("'/new' Create a new chat.")
    print_command_message("'/list' List all chats.")
    print_command_message("'/open <NUMBER>' Open chat.")
    print_command_message("'/load <PATH>/<FILE>.zip' Load ZIP backup.")
    print_command_message("'/rename <NUMBER> <NEW_NAME>' Rename chat by ID.")
    print_command_message("'/delete <NUMBER>' Delete selected chat.")
    print_command_message("'/zip' Backup contents to a timestamped zip file.")
    print_command_message("'/ingest <PATH> | <PATH><filename.json,txt,md>'"
                          "Add documents to RAG.")
    print_command_message("'/search <TERM>' Make web search with DuckDuckGo")
    print_command_message("'/restart' Restart AEON")
    print_command_message("'/quit', '/exit' or '/bye'"
                          "to end the chat.")
    


def printAeonModels():
    print_info_message(f"Models loaded:"
                       f"\nLLM: \033[36m{LLM_MODEL}\033[0m"
                       f"\nEMB: \033[36m{EMB_MODEL}\033[0m")
