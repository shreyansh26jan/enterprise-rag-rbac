import pytest

from app.db.database import SessionLocal
from app.retrieval.keyword_search import keyword_search


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def document_names(results):
    return {result["document_name"] for result in results}


def test_hr_manager_can_keyword_search_hr_policy(db):
    results = keyword_search(
        db,
        "anjali",
        "employee",
    )

    names = document_names(results)

    assert "HR Policy" in names
    assert "Engineering Architecture" not in names


def test_engineer_cannot_keyword_search_hr_policy(db):
    results = keyword_search(
        db,
        "shreyansh",
        "employee",
    )

    names = document_names(results)

    assert "HR Policy" not in names
    assert names <= {
        "Engineering Architecture",
        "Company Handbook",
    }


def test_employee_can_keyword_search_public_document(db):
    results = keyword_search(
        db,
        "raj",
        "company",
    )

    names = document_names(results)

    assert "Company Handbook" in names
    assert names <= {"Company Handbook"}


def test_unknown_user_gets_no_results(db):
    results = keyword_search(
        db,
        "unknown_user",
        "company",
    )

    assert results == []


def test_empty_query_is_rejected(db):
    with pytest.raises(ValueError, match="Query cannot be empty"):
        keyword_search(db, "raj", "   ")


def test_invalid_top_k_is_rejected(db):
    with pytest.raises(ValueError, match="top_k must be at least 1"):
        keyword_search(
            db,
            "raj",
            "company",
            top_k=0,
        )