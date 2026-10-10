from app.generation.context_builder import build_context


def test_build_context():
    results = [
        {
            "document_name": "HR Policy",
            "chunk_id": 1,
            "content": "Employees are entitled to annual leave.",
            "vector_score": 0.8,
            "keyword_score": 1.0,
            "score": 0.86,
        },
        {
            "document_name": "Company Handbook",
            "chunk_id": 2,
            "content": "Employees must follow the leave approval process.",
            "vector_score": 0.7,
            "keyword_score": 0.5,
            "score": 0.64,
        },
    ]

    context = build_context(results)

    assert "HR Policy" in context
    assert "Employees are entitled to annual leave." in context
    assert "Company Handbook" in context
    assert "leave approval process" in context


def test_build_context_empty_results():
    assert build_context([]) == ""


def test_build_context_skips_empty_content():
    results = [
        {
            "document_name": "HR Policy",
            "chunk_id": 1,
            "content": "",
        }
    ]

    assert build_context(results) == ""