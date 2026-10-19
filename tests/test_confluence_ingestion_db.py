
import pytest

from app.db.database import SessionLocal
from app.ingestion.confluence_ingestion import ingest_confluence_space
from app.models.rbac import Document, DocumentChunk, Role


@pytest.fixture
def db_session():
    session = SessionLocal()
    test_page_ids = {"1002", "1003", "1006", "1004", "1005"}

    try:
        # Clean up leftovers from previous runs of these tests.
        existing_documents = (
            session.query(Document)
            .filter(
                Document.source == "confluence",
                Document.source_id.in_(test_page_ids),
            )
            .all()
        )

        for document in existing_documents:
            session.delete(document)

        session.commit()

        yield session

    finally:
        # Ingestion commits internally, so rollback alone is insufficient.
        try:
            test_documents = (
                session.query(Document)
                .filter(
                    Document.source == "confluence",
                    Document.source_id.in_(test_page_ids),
                )
                .all()
            )

            for document in test_documents:
                session.delete(document)

            session.commit()
        finally:
            session.close()


class FakeConfluenceClient:
    base_url = "https://example.atlassian.net"

    def __init__(self, pages):
        self.pages = pages

    def get_pages(self, space_id, limit=50):
        return self.pages


def make_page(
    page_id="1001",
    title="Security Policy",
    content="Employees must protect company data. " * 20,
):
    return {
        "id": page_id,
        "title": title,
        "body": {
            "storage": {
                "value": f"<h1>{title}</h1><p>{content}</p>"
            }
        },
        "_links": {
            "webui": f"/spaces/ENG/pages/{page_id}"
        },
    }


def test_ingest_creates_document_and_chunks(db_session):
    page_id = "1002"
    page = make_page(page_id=page_id)
    client = FakeConfluenceClient([page])

    chunks_created = ingest_confluence_space(
        db=db_session,
        space_id="123",
        classification="internal",
        client=client,
    )

    assert chunks_created > 0

    document = (
        db_session.query(Document)
        .filter(
            Document.source == "confluence",
            Document.source_id == page_id,
        )
        .one()
    )

    assert document.name == "Security Policy"
    assert document.classification == "internal"
    assert document.source_url == (
        f"https://example.atlassian.net/wiki/spaces/ENG/pages/{page_id}"
    )

    chunks = (
        db_session.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .all()
    )

    assert len(chunks) == chunks_created
    assert all(chunk.content for chunk in chunks)


def test_reingestion_does_not_create_duplicate_document(db_session):
    page_id = "1003"
    page = make_page(page_id=page_id)
    client = FakeConfluenceClient([page])

    first_count = ingest_confluence_space(
        db=db_session,
        space_id="123",
        classification="internal",
        client=client,
    )

    first_document = (
        db_session.query(Document)
        .filter(
            Document.source == "confluence",
            Document.source_id == page_id,
        )
        .one()
    )
    first_document_id = first_document.id

    second_count = ingest_confluence_space(
        db=db_session,
        space_id="123",
        classification="internal",
        client=client,
    )

    documents = (
        db_session.query(Document)
        .filter(
            Document.source == "confluence",
            Document.source_id == page_id,
        )
        .all()
    )

    assert len(documents) == 1
    assert documents[0].id == first_document_id
    assert second_count == first_count


def test_changed_page_updates_existing_document(db_session):
    page_id = "1006"

    original_page = make_page(
        page_id=page_id,
        title="Old Security Policy",
        content="Original policy content. " * 20,
    )
    client = FakeConfluenceClient([original_page])

    ingest_confluence_space(
        db=db_session,
        space_id="123",
        classification="internal",
        client=client,
    )

    updated_page = make_page(
        page_id=page_id,
        title="Updated Security Policy",
        content="Updated policy content. " * 20,
    )
    client.pages = [updated_page]

    ingest_confluence_space(
        db=db_session,
        space_id="123",
        classification="confidential",
        client=client,
    )

    document = (
        db_session.query(Document)
        .filter(
            Document.source == "confluence",
            Document.source_id == page_id,
        )
        .one()
    )

    assert document.name == "Updated Security Policy"
    assert document.classification == "confidential"

    chunks = (
        db_session.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .all()
    )
    combined_content = " ".join(chunk.content for chunk in chunks)

    assert "Updated policy content." in combined_content
    assert "Original policy content." not in combined_content


def test_existing_roles_are_preserved(db_session):
    page_id = "1004"

    role = (
        db_session.query(Role)
        .filter(Role.name == "engineer")
        .one()
    )

    client = FakeConfluenceClient([make_page(page_id=page_id)])

    ingest_confluence_space(
        db=db_session,
        space_id="123",
        classification="internal",
        client=client,
    )

    document = (
        db_session.query(Document)
        .filter(
            Document.source == "confluence",
            Document.source_id == page_id,
        )
        .one()
    )

    document.roles.append(role)
    db_session.commit()

    updated_page = make_page(
        page_id=page_id,
        title="Updated Engineering Policy",
        content="Updated engineering content. " * 20,
    )
    client.pages = [updated_page]

    ingest_confluence_space(
        db=db_session,
        space_id="123",
        classification="internal",
        client=client,
    )

    db_session.refresh(document)

    assert len(document.roles) == 1
    assert document.roles[0].id == role.id


def test_new_document_has_no_roles(db_session):
    page_id = "1005"
    client = FakeConfluenceClient([make_page(page_id=page_id)])

    ingest_confluence_space(
        db=db_session,
        space_id="123",
        classification="internal",
        client=client,
    )

    document = (
        db_session.query(Document)
        .filter(
            Document.source == "confluence",
            Document.source_id == page_id,
        )
        .one()
    )

    assert document.roles == []
