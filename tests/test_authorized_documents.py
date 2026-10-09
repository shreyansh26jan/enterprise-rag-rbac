from app.auth.authorized_documents import get_authorized_documents
from app.db.database import SessionLocal


def get_document_names(documents):
    return {document.name for document in documents}


def test_hr_manager_gets_authorized_documents():
    db = SessionLocal()

    try:
        documents = get_authorized_documents(
            db,
            "anjali",
        )

        names = get_document_names(documents)

        assert "HR Policy" in names
        assert "Company Handbook" in names
        assert "Engineering Architecture" not in names

    finally:
        db.close()


def test_engineer_gets_authorized_documents():
    db = SessionLocal()

    try:
        documents = get_authorized_documents(
            db,
            "shreyansh",
        )

        names = get_document_names(documents)

        assert "Engineering Architecture" in names
        assert "Company Handbook" in names
        assert "HR Policy" not in names

    finally:
        db.close()


def test_employee_gets_only_public_document():
    db = SessionLocal()

    try:
        documents = get_authorized_documents(
            db,
            "raj",
        )

        names = get_document_names(documents)

        assert "Company Handbook" in names
        assert "HR Policy" not in names
        assert "Engineering Architecture" not in names

    finally:
        db.close()


def test_admin_gets_all_documents():
    db = SessionLocal()

    try:
        documents = get_authorized_documents(
            db,
            "admin",
        )

        names = get_document_names(documents)

        assert "HR Policy" in names
        assert "Engineering Architecture" in names
        assert "Company Handbook" in names

    finally:
        db.close()


def test_unknown_user_gets_no_documents():
    db = SessionLocal()

    try:
        documents = get_authorized_documents(
            db,
            "unknown_user",
        )

        assert documents == []

    finally:
        db.close()