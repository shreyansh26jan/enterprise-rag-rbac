
import pytest

from app.generation.rag_service import answer_question


def test_answer_question_rejects_empty_question():
    with pytest.raises(ValueError, match="Question cannot be empty."):
        answer_question(
            db=None,
            username="anjali",
            question="",
        )


def test_answer_question_rejects_whitespace_question():
    with pytest.raises(ValueError, match="Question cannot be empty."):
        answer_question(
            db=None,
            username="anjali",
            question="   ",
        )


import pytest

from app.db.database import SessionLocal
from app.generation import rag_service


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_hr_user_gets_answer_with_authorized_sources(db, monkeypatch):
    captured_prompts = []

    def fake_generate_answer(prompt):
        captured_prompts.append(prompt)
        return "Employees should consult the HR leave policy."

    monkeypatch.setattr(
        rag_service,
        "generate_answer",
        fake_generate_answer,
    )

    result = rag_service.answer_question(
        db=db,
        username="anjali",
        question="employee leave policy",
    )

    assert result["answer"] == (
        "Employees should consult the HR leave policy."
    )
    assert result["sources"]
    assert "HR Policy" in result["sources"]

    # The HR document must be available to the authorized user's prompt.
    assert len(captured_prompts) == 1
    assert "HR Policy" in captured_prompts[0]


def test_engineer_prompt_excludes_hr_content(db, monkeypatch):
    captured_prompts = []

    def fake_generate_answer(prompt):
        captured_prompts.append(prompt)
        return "I can answer using the documents available to you."

    monkeypatch.setattr(
        rag_service,
        "generate_answer",
        fake_generate_answer,
    )

    result = rag_service.answer_question(
        db=db,
        username="shreyansh",
        question="employee leave policy",
    )

    assert len(captured_prompts) == 1
    assert "HR Policy" not in result["sources"]
    assert "Human Resources Department" not in captured_prompts[0]
    assert "confidential employee" not in captured_prompts[0].lower()


def test_unknown_user_receives_no_results_without_llm_call(
    db,
    monkeypatch,
):
    def unexpected_llm_call(prompt):
        pytest.fail("LLM must not be called when retrieval returns no results.")

    monkeypatch.setattr(
        rag_service,
        "generate_answer",
        unexpected_llm_call,
    )

    result = rag_service.answer_question(
        db=db,
        username="unknown_user",
        question="company information",
    )

    assert result["sources"] == []
    assert "couldn't find relevant information" in result["answer"]    