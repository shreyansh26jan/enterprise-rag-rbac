
from langchain_ollama import OllamaEmbeddings


embeddings_model = OllamaEmbeddings(
    model="mxbai-embed-large",
)


def generate_embedding(text: str) -> list[float]:
    """Generate a vector embedding for the supplied text."""
    if not text or not text.strip():
        raise ValueError("Cannot generate an embedding for empty text.")

    return embeddings_model.embed_query(text)