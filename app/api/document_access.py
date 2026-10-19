from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.document_access_schemas import (
    DocumentRoleAssignmentRequest,
    DocumentRoleAssignmentResponse,
)
from app.auth.authorization import user_has_permission
from app.db.database import get_db
from app.models.rbac import Document, Role
from app.security.dependencies import get_current_username


DOCUMENT_MANAGE_ACCESS = "document:manage_access"


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Document Access"],
)


@router.post(
    "/{document_id}/roles",
    response_model=DocumentRoleAssignmentResponse,
)
def assign_document_role(
    document_id: int,
    request: DocumentRoleAssignmentRequest,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    """
    Assign a role to a document.

    Only users with document:manage_access permission
    can modify document access.
    """

    if not user_has_permission(
        db,
        username,
        DOCUMENT_MANAGE_ACCESS,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to manage document access.",
        )

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    role = (
        db.query(Role)
        .filter(Role.name == request.role_name)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    if role in document.roles:
        return {
            "document_id": document.id,
            "document_name": document.name,
            "role_name": role.name,
            "assigned": False,
        }

    document.roles.append(role)
    db.commit()

    return {
        "document_id": document.id,
        "document_name": document.name,
        "role_name": role.name,
        "assigned": True,
    }

@router.delete(
    "/{document_id}/roles/{role_name}",
    response_model=DocumentRoleAssignmentResponse,
)
def revoke_document_role(
    document_id: int,
    role_name: str,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    if not user_has_permission(db, username, DOCUMENT_MANAGE_ACCESS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to manage document access.",
        )

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    role_name = role_name.strip()

    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    if role not in document.roles:
        return {
            "document_id": document.id,
            "document_name": document.name,
            "role_name": role.name,
            "assigned": False,
        }

    document.roles.remove(role)
    db.commit()

    return {
        "document_id": document.id,
        "document_name": document.name,
        "role_name": role.name,
        "assigned": False,
    }