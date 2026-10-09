
from sqlalchemy.orm import Session

from app.ingestion.embedding_service import generate_embedding
from app.models.rbac import Document, DocumentChunk, Role, User


def similarity_search(
    db: Session,
    username: str,
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """Search only chunks belonging to documents the user may access."""

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    user = (
        db.query(User)
        .filter(
            User.username == username,
            User.is_active.is_(True),
        )
        .first()
    )

    if user is None or not user.roles:
        return []

    role_ids = [role.id for role in user.roles]
    query_embedding = generate_embedding(query)

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    results = (
        db.query(
            DocumentChunk,
            Document.name.label("document_name"),
            distance.label("distance"),
        )
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(
            DocumentChunk.embedding.is_not(None),
            Document.roles.any(Role.id.in_(role_ids)),
        )
        .order_by(distance)
        .limit(top_k)
        .all()
    )

    return [
        {
            "document_name": document_name,
            "chunk_id": chunk.id,
            "content": chunk.content,
            "distance": float(distance_value),
        }
        for chunk, document_name, distance_value in results
    ]