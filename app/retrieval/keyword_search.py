from sqlalchemy.orm import Session

from app.models.rbac import Document, DocumentChunk, Role, User


def keyword_search(
    db: Session,
    username: str,
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """
    Search document chunks using keyword matching.

    Only chunks belonging to documents authorized for the
    given user are returned.
    """

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

    search_pattern = f"%{query.strip()}%"

    results = (
        db.query(
            DocumentChunk,
            Document.name.label("document_name"),
        )
        .join(
            Document,
            DocumentChunk.document_id == Document.id,
        )
        .filter(
            DocumentChunk.content.ilike(search_pattern),
            Document.roles.any(Role.id.in_(role_ids)),
        )
        .limit(top_k)
        .all()
    )

    return [
        {
            "document_name": document_name,
            "chunk_id": chunk.id,
            "content": chunk.content,
        }
        for chunk, document_name in results
    ]