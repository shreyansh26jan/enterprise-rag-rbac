from pathlib import Path

from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.models.rbac import Document, DocumentChunk
from app.ingestion.text_ingestion import chunk_text


def ingest_pdf(
    db: Session,
    document_name: str,
    file_path: str,
) -> int:
    """
    Read a PDF file page by page and store its chunks
    against an existing Document.

    Returns the number of chunks created.
    """

    document = (
        db.query(Document)
        .filter(Document.name == document_name)
        .first()
    )

    if not document:
        raise ValueError(
            f"Document '{document_name}' does not exist."
        )

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file: {file_path}"
        )

    reader = PdfReader(str(path))

    # Remove existing chunks so ingestion is repeatable.
    document.chunks.clear()

    chunk_count = 0

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        chunks = chunk_text(text)

        for content in chunks:
            chunk = DocumentChunk(
                document_id=document.id,
                content=content,
                chunk_index=chunk_count,
                page_number=page_number,
            )

            db.add(chunk)

            chunk_count += 1

    db.commit()

    return chunk_count