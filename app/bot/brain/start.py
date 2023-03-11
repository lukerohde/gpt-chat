import os
import signal

from config import Config
from chatgpt import ChatGPT
from trello import Trello 
from long_term_memory import LongTermMemory
from working_memory import WorkingMemory
from application import Application


def _primer():
    result = ""
    with open(os.getenv("PRIMER_FILE"), "r") as f:
        result = f.read()
    return result

user = os.getenv("USER_NAME") or "User"
config = Config(
    botname = os.getenv("BOT_NAME"),
    primer = _primer(),
    openai_response_tokens = os.getenv("OPENAI_RESPONSE_TOKENS") or 256, 
    openai_max_tokens = os.getenv("OPENAI_MAX_TOKENS") or 4000, 
    openai_token_length = os.getenv("OPENAI_TOKENS_LENGTH") or 3.5, 
    editor = os.getenv("EDITOR") or "nano", 
    bot = ChatGPT(
        os.getenv("OPENAI_API_KEY"), 
        os.getenv("OPENAI_COMPLETION_MODEL") or "text-davinci-003", 
        os.getenv("OPENAI_TEMPERATURE") or "0.8", 
        os.getenv("OPENAI_RESPONSE_TOKENS") or 256),
    trello=Trello(os.getenv("TRELLO_ENDPOINT"), os.getenv("TRELLO_API_KEY"), os.getenv("TRELLO_TOKEN")),
    long_term_memory=LongTermMemory(os.getenv("OPENAI_API_KEY"), os.getenv("OPENAI_EMBEDDING_MODEL") or "text-embedding-ada-002", os.getenv("BOT_NAME"), user),
)

working_memory = WorkingMemory(config, user)

app = Application(config, working_memory)

def handle_exit(signal, frame):
    print("\nShutting down...")
    raise SystemExit

signal.signal(signal.SIGINT, handle_exit) # ctrl+c
signal.signal(signal.SIGTERM, handle_exit) # kill signal

app.go()

