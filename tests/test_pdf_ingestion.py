from uuid import uuid4

import pytest
from reportlab.pdfgen import canvas

from app.db.database import SessionLocal
from app.ingestion.pdf_ingestion import ingest_pdf
from app.models.rbac import Document


@pytest.fixture
def db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def document(db):
    doc = Document(
        name=f"PDF Test Document {uuid4().hex}",
        source="test",
        classification="public",
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    yield doc

    # Remove the test document and its chunks.
    db.delete(doc)
    db.commit()


def create_pdf(path, pages):
    """Create a test PDF from a list of page strings."""
    pdf = canvas.Canvas(str(path))

    for text in pages:
        if text:
            pdf.drawString(72, 720, text)

        pdf.showPage()

    pdf.save()


def test_pdf_ingestion_stores_page_numbers(
    db,
    document,
    tmp_path,
):
    pdf_path = tmp_path / "sample.pdf"

    create_pdf(
        pdf_path,
        [
            "This is content from page one.",
            "This is content from page two.",
        ],
    )

    count = ingest_pdf(
        db,
        document.name,
        str(pdf_path),
    )

    db.refresh(document)

    chunks = sorted(
        document.chunks,
        key=lambda chunk: chunk.chunk_index,
    )

    assert count == 2
    assert len(chunks) == 2
    assert chunks[0].page_number == 1
    assert chunks[1].page_number == 2
    assert "page one" in chunks[0].content
    assert "page two" in chunks[1].content


def test_pdf_reingestion_replaces_existing_chunks(
    db,
    document,
    tmp_path,
):
    pdf_path = tmp_path / "sample.pdf"

    create_pdf(
        pdf_path,
        [
            "Original page one.",
            "Original page two.",
        ],
    )

    first_count = ingest_pdf(
        db,
        document.name,
        str(pdf_path),
    )

    create_pdf(
        pdf_path,
        ["Updated document content."],
    )

    second_count = ingest_pdf(
        db,
        document.name,
        str(pdf_path),
    )

    db.refresh(document)

    assert first_count == 2
    assert second_count == 1
    assert len(document.chunks) == 1
    assert "Updated document content" in document.chunks[0].content
    assert document.chunks[0].page_number == 1


def test_pdf_ingestion_rejects_missing_file(
    db,
    document,
    tmp_path,
):
    missing_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        ingest_pdf(
            db,
            document.name,
            str(missing_path),
        )


def test_pdf_ingestion_rejects_unknown_document(
    db,
    tmp_path,
):
    pdf_path = tmp_path / "sample.pdf"
    create_pdf(pdf_path, ["Sample content."])

    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        ingest_pdf(
            db,
            "Nonexistent Document",
            str(pdf_path),
        )


def test_pdf_ingestion_rejects_non_pdf_file(
    db,
    document,
    tmp_path,
):
    text_path = tmp_path / "sample.txt"
    text_path.write_text(
        "This is not a PDF.",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Expected a PDF file",
    ):
        ingest_pdf(
            db,
            document.name,
            str(text_path),
        )


def test_pdf_ingestion_skips_empty_pages(
    db,
    document,
    tmp_path,
):
    pdf_path = tmp_path / "sample.pdf"

    create_pdf(
        pdf_path,
        [
            "Content on page one.",
            "",
            "Content on page three.",
        ],
    )

    count = ingest_pdf(
        db,
        document.name,
        str(pdf_path),
    )

    db.refresh(document)

    chunks = sorted(
        document.chunks,
        key=lambda chunk: chunk.chunk_index,
    )

    assert count == 2
    assert len(chunks) == 2
    assert chunks[0].page_number == 1
    assert chunks[1].page_number == 3