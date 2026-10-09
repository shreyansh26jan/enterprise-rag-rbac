from sqlalchemy.orm import Session

from app.retrieval.keyword_search import keyword_search
from app.retrieval.vector_search import similarity_search


def hybrid_search(
    db: Session,
    username: str,
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """
    Combine vector and keyword search results.

    Both underlying searches enforce RBAC independently,
    so unauthorized documents are never introduced into
    the hybrid result set.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    vector_results = similarity_search(
        db,
        username,
        query,
        top_k=top_k,
    )

    keyword_results = keyword_search(
        db,
        username,
        query,
        top_k=top_k,
    )

    combined = {}

    # Add vector results.
    for rank, result in enumerate(vector_results):
        chunk_id = result["chunk_id"]

        # Convert cosine distance into a similarity score.
        vector_score = 1 / (1 + result["distance"])

        combined[chunk_id] = {
            "document_name": result["document_name"],
            "chunk_id": chunk_id,
            "content": result["content"],
            "vector_score": vector_score,
            "keyword_score": 0.0,
        }

    # Add keyword results.
    for rank, result in enumerate(keyword_results):
        chunk_id = result["chunk_id"]

        # Higher score for higher-ranked keyword results.
        keyword_score = 1 / (rank + 1)

        if chunk_id not in combined:
            combined[chunk_id] = {
                "document_name": result["document_name"],
                "chunk_id": chunk_id,
                "content": result["content"],
                "vector_score": 0.0,
                "keyword_score": keyword_score,
            }
        else:
            combined[chunk_id]["keyword_score"] = keyword_score

    # Weighted hybrid score.
    for result in combined.values():
        result["score"] = (
            0.7 * result["vector_score"]
            + 0.3 * result["keyword_score"]
        )

    results = sorted(
        combined.values(),
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]