from langchain_community.llms import Ollama
from langchain_openai import OpenAI

def load_model(config):
    if config["MODEL_PROVIDER"] == "ollama":
        return Ollama(model=config["OLLAMA_MODEL"])
    elif config["MODEL_PROVIDER"] == "openai":
        return OpenAI(openai_api_key=config["OPENAI_API_KEY"])
    else:
        raise ValueError("Unsupported MODEL_PROVIDER")
