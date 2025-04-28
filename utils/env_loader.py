from dotenv import load_dotenv
import os

def load_env():
    load_dotenv()
    return {
        "MODEL_PROVIDER": os.getenv("MODEL_PROVIDER", "ollama"),
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "llama3"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    }
