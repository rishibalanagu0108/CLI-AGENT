import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

MAX_TOKENS      = 4096
MAX_ITERATIONS  = 10

SYSTEM_PROMPT = (
    "You are a helpful AI assistant with access to tools. "
    "Use them when needed to answer questions accurately. "
    "Think carefully about which tools to use and in what order."
)
