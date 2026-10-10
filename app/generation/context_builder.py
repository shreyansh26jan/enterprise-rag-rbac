def build_context(results: list[dict]) -> str:
    """
    Build an LLM-ready context from hybrid search results.

    Only the content and document name are included in the
    context sent to the language model.
    """

    if not results:
        return ""

    context_parts = []

    for result in results:
        document_name = result.get("document_name", "Unknown Document")
        content = result.get("content", "").strip()

        if not content:
            continue

        context_parts.append(
            f"Source: {document_name}\n"
            f"Content:\n{content}"
        )

    return "\n\n---\n\n".join(context_parts)