from sqlalchemy.orm import Session

from app.models.rbac import User, Role, Document, DocumentChunk


def get_authorized_chunks(
    db: Session,
    username: str,
):
    """
    Return only chunks belonging to documents
    that the user is authorized to access.
    """

    user = (
        db.query(User)
        .filter(
            User.username == username,
            User.is_active.is_(True),
        )
        .first()
    )

    if not user:
        return []

    role_ids = [role.id for role in user.roles]

    if not role_ids:
        return []

    chunks = (
        db.query(DocumentChunk)
        .join(Document)
        .filter(
            Document.roles.any(
                Role.id.in_(role_ids)
            )
        )
        .all()
    )

    return chunks