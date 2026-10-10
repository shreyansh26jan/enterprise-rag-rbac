from app.generation.context_builder import build_context
from app.generation.prompt import RAG_SYSTEM_PROMPT


def build_rag_prompt(
    results: list[dict],
    question: str,
) -> str:
    """
    Build the final prompt that will be sent to the LLM.

    The results supplied to this function must already have
    passed through RBAC-aware retrieval.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    context = build_context(results)

    if not context:
        context = "No relevant authorized documents were found."

    return RAG_SYSTEM_PROMPT.format(
        context=context,
        question=question.strip(),
    )