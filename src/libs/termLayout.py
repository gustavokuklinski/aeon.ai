from src.config import (
    LLM_MODEL,
    EMB_MODEL
)
from src.libs.messages import print_command_message, print_info_message


def printAeonLayout():
    print("                                    ")
    print("\033[38;5;196m █████╗ ███████╗ ██████╗ ███╗   ██╗ \033[0m")
    print("\033[38;5;197m██╔══██╗██╔════╝██╔═══██╗████╗  ██║ \033[0m")
    print("\033[38;5;160m███████║█████╗  ██║   ██║██╔██╗ ██║ \033[0m")
    print("\033[38;5;124m██╔══██║██╔══╝  ██║   ██║██║╚██╗██║ \033[0m")
    print("\033[38;5;88m██║  ██║███████╗╚██████╔╝██║ ╚████║ \033[0m")
    print("\033[38;5;52m╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ \033[0m")


def printAeonCmd():
    print("Commands to use:")
    print_command_message("'/help' show this screen.")
    print_command_message("'/new' Create a new chat.")
    print_command_message("'/list' list all chats.")
    print_command_message("'/open <NUMBER>' open chat.")
    print_command_message("'/load <NUMBER>' ingest previous chat.")
    print_command_message("'/delete <NUMBER>' Delete selected chat.")
    print_command_message("'/ingest <PATH> | <PATH><filename.json,txt,md>'"
                          "to add documents to RAG.")
    print_command_message("'/zip' backup contents to a timestamped zip file.")
    print_command_message("'/search' <TERM>' make web search with DuckDuckGo")
    print_command_message("'/quit', '/exit' or '/bye'"
                          "to end the chat.")


def printAeonModels():
    print_info_message(f"Models loaded:"
                       f"\nLLM: \033[36m{LLM_MODEL}\033[0m"
                       f"\nEMB: \033[36m{EMB_MODEL}\033[0m")
