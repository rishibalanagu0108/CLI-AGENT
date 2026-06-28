import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

MAX_TOKENS      = 4096
MAX_ITERATIONS  = 10

SYSTEM_PROMPT = (
    "You are a helpful AI assistant with access to tools. "
    "Use them when needed to answer questions accurately. "
    "Think carefully about which tools to use and in what order."
)
