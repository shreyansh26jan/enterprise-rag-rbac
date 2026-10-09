from app.db.database import SessionLocal
from app.ingestion.text_ingestion import ingest_document


def run_ingestion():
    db = SessionLocal()

    try:
        results = {
            "HR Policy": "data/sample/hr.txt",
            "Engineering Architecture": "data/sample/engineering.txt",
            "Company Handbook": "data/sample/public.txt",
        }

        for document_name, file_path in results.items():
            count = ingest_document(
                db,
                document_name,
                file_path,
            )

            print(
                f"{document_name}: {count} chunks created"
            )

    finally:
        db.close()


if __name__ == "__main__":
    run_ingestion()