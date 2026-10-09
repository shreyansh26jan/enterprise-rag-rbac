
import pytest

from app.db.database import SessionLocal
from app.retrieval.vector_search import similarity_search


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def document_names(results):
    return {result["document_name"] for result in results}


def test_hr_manager_cannot_retrieve_engineering(db):
    results = similarity_search(
        db, "anjali", "engineering system architecture"
    )
    names = document_names(results)

    assert "Engineering Architecture" not in names
    assert names <= {"HR Policy", "Company Handbook"}


def test_engineer_cannot_retrieve_hr_policy(db):
    results = similarity_search(
        db, "shreyansh", "employee leave and HR policies"
    )
    names = document_names(results)

    assert "HR Policy" not in names
    assert names <= {
        "Engineering Architecture",
        "Company Handbook",
    }


def test_employee_can_retrieve_only_public_document(db):
    results = similarity_search(
        db, "raj", "company information"
    )
    names = document_names(results)

    assert names <= {"Company Handbook"}
    assert "Company Handbook" in names


def test_unknown_user_gets_no_results(db):
    results = similarity_search(
        db, "unknown_user", "company information"
    )

    assert results == []


def test_empty_query_is_rejected(db):
    with pytest.raises(ValueError, match="Query cannot be empty"):
        similarity_search(db, "raj", "   ")


def test_invalid_top_k_is_rejected(db):
    with pytest.raises(ValueError, match="top_k must be at least 1"):
        similarity_search(db, "raj", "company information", top_k=0)