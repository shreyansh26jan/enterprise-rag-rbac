
from sqlalchemy.orm import Session

from app.generation.generator import build_rag_prompt
from app.generation.llm_service import generate_answer
from app.retrieval.hybrid_search import hybrid_search


def answer_question(
    db: Session,
    username: str,
    question: str,
    top_k: int = 3,
) -> dict:
    """
    Answer a question using RBAC-aware hybrid retrieval
    and the configured LLM.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    results = hybrid_search(
        db=db,
        username=username,
        query=question.strip(),
        top_k=top_k,
    )

    if not results:
        return {
            "answer": (
                "I couldn't find relevant information in "
                "the documents you are authorized to access."
            ),
            "sources": [],
        }

    prompt = build_rag_prompt(
        results=results,
        question=question.strip(),
    )

    answer = generate_answer(prompt)

    sources = list(
        dict.fromkeys(
            result["document_name"]
            for result in results
            if result.get("document_name")
        )
    )

    return {
        "answer": answer,
        "sources": sources,
    }