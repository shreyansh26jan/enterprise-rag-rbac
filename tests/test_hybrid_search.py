import pytest

from app.db.database import SessionLocal
from app.retrieval.hybrid_search import hybrid_search


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def document_names(results):
    return {result["document_name"] for result in results}


def test_hr_manager_can_hybrid_search_hr_content(db):
    results = hybrid_search(
        db,
        "anjali",
        "employee leave policy",
    )

    names = document_names(results)

    assert "HR Policy" in names
    assert "Engineering Architecture" not in names


def test_engineer_cannot_hybrid_search_hr_content(db):
    results = hybrid_search(
        db,
        "shreyansh",
        "employee leave policy",
    )

    names = document_names(results)

    assert "HR Policy" not in names
    assert names <= {
        "Engineering Architecture",
        "Company Handbook",
    }


def test_employee_can_hybrid_search_public_content(db):
    results = hybrid_search(
        db,
        "raj",
        "company information",
    )

    names = document_names(results)

    assert "Company Handbook" in names
    assert names <= {"Company Handbook"}


def test_unknown_user_gets_no_results(db):
    results = hybrid_search(
        db,
        "unknown_user",
        "company information",
    )

    assert results == []


def test_empty_query_is_rejected(db):
    with pytest.raises(ValueError, match="Query cannot be empty"):
        hybrid_search(db, "raj", "   ")


def test_invalid_top_k_is_rejected(db):
    with pytest.raises(ValueError, match="top_k must be at least 1"):
        hybrid_search(
            db,
            "raj",
            "company information",
            top_k=0,
        )


def test_results_are_ranked_by_score(db):
    results = hybrid_search(
        db,
        "raj",
        "company information",
    )

    scores = [result["score"] for result in results]

    assert scores == sorted(scores, reverse=True)