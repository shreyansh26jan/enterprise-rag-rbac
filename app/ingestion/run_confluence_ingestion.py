
import os

from dotenv import load_dotenv

from app.db.database import SessionLocal
from app.ingestion.confluence_client import ConfluenceClient
from app.ingestion.confluence_ingestion import ingest_confluence_space
from app.ingestion.embedding_service import generate_embedding
from app.models.rbac import Document, DocumentChunk

load_dotenv()


def main():
    space_id = os.getenv("CONFLUENCE_SPACE_ID")
    classification = os.getenv("CONFLUENCE_CLASSIFICATION", "internal")

    if not space_id:
        raise ValueError(
            "CONFLUENCE_SPACE_ID is not configured in .env"
        )

    db = SessionLocal()

    try:
        client = ConfluenceClient()

        chunks_created = ingest_confluence_space(
            db=db,
            space_id=space_id,
            classification=classification,
            client=client,
        )

        print(
            f"Confluence ingestion completed. "
            f"Chunks created: {chunks_created}"
        )

        # Embed only chunks belonging to Confluence documents
        # whose embeddings are currently missing.
        chunks = (
            db.query(DocumentChunk)
            .join(
                Document,
                DocumentChunk.document_id == Document.id,
            )
            .filter(
                Document.source == "confluence",
                DocumentChunk.embedding.is_(None),
            )
            .all()
        )

        embedded_count = 0

        for chunk in chunks:
            chunk.embedding = generate_embedding(chunk.content)
            embedded_count += 1
            print(f"Chunks embed completed for : {embedded_count}")

        db.commit()

        print(
            f"Confluence embedding completed. "
            f"Chunks embedded: {embedded_count}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
