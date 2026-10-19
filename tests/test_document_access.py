import pytest

from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.main import app
from app.models.rbac import Document, DocumentChunk, Role
from app.security.authentication import create_access_token


client = TestClient(app)


def auth_headers(username: str) -> dict[str, str]:
    token = create_access_token(username)
    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture
def db_session():
    session = SessionLocal()
    test_page_id = "document-access-test-1101"

    try:
        existing_document = (
            session.query(Document)
            .filter(
                Document.source == "confluence",
                Document.source_id == test_page_id,
            )
            .first()
        )

        if existing_document:
            session.delete(existing_document)
            session.commit()

        yield session

    finally:
        try:
            test_document = (
                session.query(Document)
                .filter(
                    Document.source == "confluence",
                    Document.source_id == test_page_id,
                )
                .first()
            )

            if test_document:
                session.delete(test_document)
                session.commit()
        finally:
            session.close()


@pytest.fixture
def roleless_document(db_session):
    document = Document(
        name="Document Access Test Policy",
        source="confluence",
        source_id="document-access-test-1101",
        source_url="https://example.atlassian.net/wiki/spaces/ENG/pages/1101",
        classification="internal",
    )

    db_session.add(document)
    db_session.flush()

    chunk = DocumentChunk(
        document_id=document.id,
        content="Engineering access control test document.",
        chunk_index=0,
    )

    db_session.add(chunk)
    db_session.commit()
    db_session.refresh(document)

    return document


def test_roleless_document_is_not_retrievable(
    db_session,
    roleless_document,
):
    from app.retrieval.authorized_retrieval import get_authorized_chunks

    chunks = get_authorized_chunks(
        db_session,
        "shreyansh",
    )

    assert all(
        chunk.document_id != roleless_document.id
        for chunk in chunks
    )


def test_authorized_user_can_assign_role(
    db_session,
    roleless_document,
):
    response = client.post(
        f"/api/v1/documents/{roleless_document.id}/roles",
        headers=auth_headers("admin"),
        json={
            "role_name": "engineer",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "document_id": roleless_document.id,
        "document_name": "Document Access Test Policy",
        "role_name": "engineer",
        "assigned": True,
    }

    db_session.refresh(roleless_document)

    assert [role.name for role in roleless_document.roles] == [
        "engineer"
    ]


def test_user_with_assigned_role_can_retrieve_document(
    db_session,
    roleless_document,
):
    from app.retrieval.authorized_retrieval import get_authorized_chunks

    role = (
        db_session.query(Role)
        .filter(Role.name == "engineer")
        .one()
    )

    roleless_document.roles.append(role)
    db_session.commit()

    chunks = get_authorized_chunks(
        db_session,
        "shreyansh",
    )

    assert any(
        chunk.document_id == roleless_document.id
        for chunk in chunks
    )


def test_user_without_assigned_role_cannot_retrieve_document(
    db_session,
    roleless_document,
):
    from app.retrieval.authorized_retrieval import get_authorized_chunks

    role = (
        db_session.query(Role)
        .filter(Role.name == "engineer")
        .one()
    )

    roleless_document.roles.append(role)
    db_session.commit()

    chunks = get_authorized_chunks(
        db_session,
        "raj",
    )

    assert all(
        chunk.document_id != roleless_document.id
        for chunk in chunks
    )


def test_unauthorized_user_cannot_modify_document_access(
    roleless_document,
):
    response = client.post(
        f"/api/v1/documents/{roleless_document.id}/roles",
        headers=auth_headers("raj"),
        json={
            "role_name": "engineer",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You are not authorized to manage document access."
    )


def test_assigning_same_role_is_idempotent(
    db_session,
    roleless_document,
):
    first_response = client.post(
        f"/api/v1/documents/{roleless_document.id}/roles",
        headers=auth_headers("admin"),
        json={
            "role_name": "engineer",
        },
    )

    second_response = client.post(
        f"/api/v1/documents/{roleless_document.id}/roles",
        headers=auth_headers("admin"),
        json={
            "role_name": "engineer",
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert first_response.json()["assigned"] is True
    assert second_response.json()["assigned"] is False

    db_session.refresh(roleless_document)

    assert [
        role.name
        for role in roleless_document.roles
        if role.name == "engineer"
    ] == ["engineer"]

def test_admin_can_revoke_document_role(
    db_session,
    roleless_document,
):
    # Assign the role first.
    assign_response = client.post(
        f"/api/v1/documents/{roleless_document.id}/roles",
        headers=auth_headers("admin"),
        json={
            "role_name": "engineer",
        },
    )

    assert assign_response.status_code == 200
    assert assign_response.json()["assigned"] is True

    # Revoke the role.
    response = client.delete(
        f"/api/v1/documents/{roleless_document.id}/roles/engineer",
        headers=auth_headers("admin"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "document_id": roleless_document.id,
        "document_name": "Document Access Test Policy",
        "role_name": "engineer",
        "assigned": False,
    }

    db_session.refresh(roleless_document)

    assert [
        role.name
        for role in roleless_document.roles
        if role.name == "engineer"
    ] == []


def test_revoked_role_removes_document_access(
    db_session,
    roleless_document,
):
    from app.retrieval.authorized_retrieval import get_authorized_chunks

    # Assign engineer role.
    assign_response = client.post(
        f"/api/v1/documents/{roleless_document.id}/roles",
        headers=auth_headers("admin"),
        json={
            "role_name": "engineer",
        },
    )

    assert assign_response.status_code == 200

    # Engineer can access before revocation.
    chunks = get_authorized_chunks(
        db_session,
        "shreyansh",
    )

    assert any(
        chunk.document_id == roleless_document.id
        for chunk in chunks
    )

    # Revoke engineer role.
    revoke_response = client.delete(
        f"/api/v1/documents/{roleless_document.id}/roles/engineer",
        headers=auth_headers("admin"),
    )

    assert revoke_response.status_code == 200

    # Engineer can no longer access the document.
    chunks = get_authorized_chunks(
        db_session,
        "shreyansh",
    )

    assert all(
        chunk.document_id != roleless_document.id
        for chunk in chunks
    )


def test_non_admin_cannot_revoke_document_role(
    db_session,
    roleless_document,
):
    # Give the document the engineer role first.
    assign_response = client.post(
        f"/api/v1/documents/{roleless_document.id}/roles",
        headers=auth_headers("admin"),
        json={
            "role_name": "engineer",
        },
    )

    assert assign_response.status_code == 200

    # Employee attempts to revoke it.
    response = client.delete(
        f"/api/v1/documents/{roleless_document.id}/roles/engineer",
        headers=auth_headers("raj"),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You are not authorized to manage document access."
    )

    # Role must still exist.
    db_session.refresh(roleless_document)

    assert [
        role.name
        for role in roleless_document.roles
        if role.name == "engineer"
    ] == ["engineer"]


def test_revoke_unassigned_role_is_idempotent(
    db_session,
    roleless_document,
):
    # engineer is intentionally NOT assigned.
    response = client.delete(
        f"/api/v1/documents/{roleless_document.id}/roles/engineer",
        headers=auth_headers("admin"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "document_id": roleless_document.id,
        "document_name": "Document Access Test Policy",
        "role_name": "engineer",
        "assigned": False,
    }