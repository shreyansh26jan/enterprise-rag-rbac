from sqlalchemy.orm import Session

from app.models.rbac import User, Document


def get_authorized_documents(
    db: Session,
    username: str,
):
    """
    Return only documents that the user is authorized to access.
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

    documents = (
        db.query(Document)
        .join(Document.roles)
        .filter(
            Document.roles.any(
                id__in=role_ids
            )
        )
        .distinct()
        .all()
    )

    return documents