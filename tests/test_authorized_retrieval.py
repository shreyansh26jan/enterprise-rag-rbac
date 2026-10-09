from app.db.database import SessionLocal
from app.retrieval.authorized_retrieval import get_authorized_chunks


def get_document_names(chunks):
    return {chunk.document.name for chunk in chunks}


def test_hr_manager_only_retrieves_authorized_chunks():
    db = SessionLocal()

    try:
        chunks = get_authorized_chunks(
            db,
            "anjali",
        )

        names = get_document_names(chunks)

        assert "HR Policy" in names
        assert "Company Handbook" in names
        assert "Engineering Architecture" not in names

    finally:
        db.close()


def test_engineer_only_retrieves_authorized_chunks():
    db = SessionLocal()

    try:
        chunks = get_authorized_chunks(
            db,
            "shreyansh",
        )

        names = get_document_names(chunks)

        assert "Engineering Architecture" in names
        assert "Company Handbook" in names
        assert "HR Policy" not in names

    finally:
        db.close()


def test_employee_only_retrieves_public_chunks():
    db = SessionLocal()

    try:
        chunks = get_authorized_chunks(
            db,
            "raj",
        )

        names = get_document_names(chunks)

        assert "Company Handbook" in names
        assert "HR Policy" not in names
        assert "Engineering Architecture" not in names

    finally:
        db.close()


def test_admin_retrieves_all_chunks():
    db = SessionLocal()

    try:
        chunks = get_authorized_chunks(
            db,
            "admin",
        )

        names = get_document_names(chunks)

        assert "HR Policy" in names
        assert "Engineering Architecture" in names
        assert "Company Handbook" in names

    finally:
        db.close()


def test_unknown_user_retrieves_no_chunks():
    db = SessionLocal()

    try:
        chunks = get_authorized_chunks(
            db,
            "unknown_user",
        )

        assert chunks == []

    finally:
        db.close()