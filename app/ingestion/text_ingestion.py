from pathlib import Path

from sqlalchemy.orm import Session

from app.models.rbac import Document, DocumentChunk


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Split text into overlapping character-based chunks.
    """

    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    text = text.strip()

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def ingest_document(
    db: Session,
    document_name: str,
    file_path: str,
) -> int:
    """
    Read a text file and store its chunks against an existing Document.

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

    text = path.read_text(encoding="utf-8")

    chunks = chunk_text(text)

    # Remove existing chunks so ingestion is repeatable.
    document.chunks.clear()

    for index, content in enumerate(chunks):
        chunk = DocumentChunk(
            document_id=document.id,
            content=content,
            chunk_index=index,
        )

        db.add(chunk)

    db.commit()

    return len(chunks)