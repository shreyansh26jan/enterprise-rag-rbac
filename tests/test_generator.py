import pytest

from app.generation.generator import build_rag_prompt


def test_build_rag_prompt():
    results = [
        {
            "document_name": "HR Policy",
            "chunk_id": 1,
            "content": "Employees are entitled to annual leave.",
        }
    ]

    prompt = build_rag_prompt(
        results,
        "What is the annual leave policy?",
    )

    assert "HR Policy" in prompt
    assert "Employees are entitled to annual leave." in prompt
    assert "What is the annual leave policy?" in prompt


def test_build_rag_prompt_with_no_results():
    prompt = build_rag_prompt(
        [],
        "What is the leave policy?",
    )

    assert "No relevant authorized documents were found." in prompt


def test_build_rag_prompt_rejects_empty_question():
    with pytest.raises(ValueError, match="Question cannot be empty."):
        build_rag_prompt([], "")


def test_build_rag_prompt_strips_question():
    prompt = build_rag_prompt(
        [],
        "   What is the leave policy?   ",
    )

    assert "What is the leave policy?" in prompt