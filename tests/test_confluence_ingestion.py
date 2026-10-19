
from unittest.mock import Mock

import pytest

from app.ingestion.confluence_ingestion import (
    extract_page_text,
    ingest_confluence_space,
)
from app.models.rbac import Document, DocumentChunk


def test_extract_page_text():
    page = {
        "body": {
            "storage": {
                "value": (
                    "<h1>Security Policy</h1>"
                    "<p>Employees must protect company data.</p>"
                    "<script>ignore_this()</script>"
                )
            }
        }
    }

    text = extract_page_text(page)

    assert "Security Policy" in text
    assert "Employees must protect company data." in text
    assert "ignore_this" not in text


def test_extract_page_text_empty_body():
    assert extract_page_text({"body": {}}) == ""


def test_ingest_rejects_empty_space_id():
    db = Mock()

    with pytest.raises(ValueError, match="space_id"):
        ingest_confluence_space(
            db=db,
            space_id=" ",
            classification="internal",
        )


def test_ingest_rejects_invalid_limit():
    db = Mock()

    with pytest.raises(ValueError, match="limit"):
        ingest_confluence_space(
            db=db,
            space_id="123",
            classification="internal",
            client=Mock(),
            limit=0,
        )
