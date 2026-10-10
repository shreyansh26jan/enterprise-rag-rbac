from app.generation.prompt import RAG_SYSTEM_PROMPT


def test_rag_prompt_contains_required_placeholders():
    assert "{context}" in RAG_SYSTEM_PROMPT
    assert "{question}" in RAG_SYSTEM_PROMPT


def test_rag_prompt_contains_grounding_rules():
    assert "ONLY the information provided" in RAG_SYSTEM_PROMPT
    assert "Do not invent" in RAG_SYSTEM_PROMPT
    assert "outside knowledge" in RAG_SYSTEM_PROMPT


def test_rag_prompt_mentions_sources():
    assert "source document names" in RAG_SYSTEM_PROMPT