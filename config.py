import os
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_API_KEY     = os.environ.get("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT    = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT  = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

MAX_TOKENS      = 4096
MAX_ITERATIONS  = 10

SYSTEM_PROMPT = (
    "You are a helpful AI assistant with access to tools. "
    "Use them when needed to answer questions accurately. "
    "Think carefully about which tools to use and in what order."
)
