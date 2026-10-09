
from app.db.database import SessionLocal
from app.models.rbac import DocumentChunk
from app.ingestion.embedding_service import generate_embedding


def embed_chunks() -> None:
    db = SessionLocal()

    try:
        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.embedding.is_(None))
            .all()
        )

        print(f"Chunks requiring embeddings: {len(chunks)}")

        for chunk in chunks:
            chunk.embedding = generate_embedding(chunk.content)
            print(f"Embedded chunk ID: {chunk.id}")

        db.commit()
        print("Embedding generation completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    embed_chunks()