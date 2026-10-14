from app.db.database import SessionLocal
from app.ingestion.pdf_ingestion import ingest_pdf


def run_pdf_ingestion(
    document_name: str,
    file_path: str,
) -> None:
    db = SessionLocal()

    try:
        count = ingest_pdf(
            db=db,
            document_name=document_name,
            file_path=file_path,
        )

        print(
            f"{document_name}: {count} PDF chunks created"
        )

    finally:
        db.close()


# if __name__ == "__main__":
#     run_pdf_ingestion(
#         document_name="PDF Test Document",
#         file_path="data/sample/sample.pdf",
#     )
if __name__ == "__main__":
    run_pdf_ingestion(
        document_name="IIMA HR Policy Manual 2026",
        file_path="data/sample/sample.pdf",
    )    