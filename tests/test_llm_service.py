
import pytest

from app.generation.llm_service import generate_answer, get_llm


def test_get_llm_uses_configured_model():
    llm = get_llm()

    assert llm.model == "gemma3:1b"
    assert llm.temperature == 0


def test_generate_answer_rejects_empty_prompt():
    with pytest.raises(ValueError, match="Prompt cannot be empty."):
        generate_answer("")


def test_generate_answer_rejects_whitespace_prompt():
    with pytest.raises(ValueError, match="Prompt cannot be empty."):
        generate_answer("   ")