from sqlalchemy.orm import Session

from app.models.rbac import User, Document


def user_has_permission(
    db: Session,
    username: str,
    permission_name: str,
) -> bool:
    """
    Check whether a user has a specific permission.
    """

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user or not user.is_active:
        return False

    for role in user.roles:
        for permission in role.permissions:
            if permission.name == permission_name:
                return True

    return False


def user_can_access_document(
    db: Session,
    username: str,
    document_name: str,
) -> bool:
    """
    Check whether a user can access a specific document.
    """

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user or not user.is_active:
        return False

    document = (
        db.query(Document)
        .filter(Document.name == document_name)
        .first()
    )

    if not document:
        return False

    user_roles = {role.id for role in user.roles}
    document_roles = {role.id for role in document.roles}

    return bool(user_roles & document_roles)