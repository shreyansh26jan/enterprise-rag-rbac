import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

def get_llm() -> ChatOllama:
    """
    Create the local Ollama chat model.

    OLLAMA_MODEL can be configured through the environment.
    """

    model_name = os.getenv("LLM_MODEL")

    if not model_name:
        raise ValueError(
            "OLLAMA_MODEL is not configured."
        )

    return ChatOllama(
        model=model_name,
        temperature=0,
    )


def generate_answer(prompt: str) -> str:
    """
    Generate an answer using the configured Ollama model.
    """

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    llm = get_llm()
    response = llm.invoke(prompt)

    return response.content