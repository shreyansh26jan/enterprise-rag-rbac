
from html.parser import HTMLParser
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.ingestion.confluence_client import ConfluenceClient
from app.ingestion.text_ingestion import chunk_text
from app.models.rbac import Document, DocumentChunk


class _HTMLTextExtractor(HTMLParser):
    """Extract readable text from Confluence storage HTML."""

    BLOCK_TAGS = {
        "p", "div", "br", "li", "ul", "ol",
        "h1", "h2", "h3", "h4", "h5", "h6",
        "tr", "td", "th", "blockquote", "pre",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip_depth += 1
        elif self.skip_depth == 0 and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.skip_depth:
            self.skip_depth -= 1
        elif self.skip_depth == 0 and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.parts.append(data)

    def get_text(self):
        lines = [
            " ".join(line.split())
            for line in "".join(self.parts).splitlines()
        ]
        return "\n".join(line for line in lines if line).strip()


def extract_page_text(page: dict) -> str:
    """Extract plain text from a Confluence page response."""

    body = page.get("body") or {}
    storage = body.get("storage") or {}
    html = storage.get("value") or ""

    parser = _HTMLTextExtractor()
    parser.feed(html)
    parser.close()

    return parser.get_text()


def _page_url(client: ConfluenceClient, page: dict) -> str | None:
    """Build a browser URL for a Confluence page."""

    webui = (page.get("_links") or {}).get("webui")

    if not webui:
        return None

    parsed = urlparse(webui)

    # Do not trust an API-provided absolute URL to point to another host.
    if parsed.scheme or parsed.netloc:
        configured_host = urlparse(client.base_url).netloc
        if parsed.netloc != configured_host or parsed.scheme != "https":
            return None
        return webui

    if not webui.startswith("/"):
        return None

    return f"{client.base_url}/wiki{webui}"


def ingest_confluence_space(
    db: Session,
    space_id: str,
    classification: str,
    client: ConfluenceClient | None = None,
    limit: int = 50,
) -> int:
    """
    Ingest pages from a Confluence space into the existing RAG tables.

    Existing documents are matched by source + stable Confluence page ID.
    Updating a page replaces its chunks but preserves its role assignments.
    New documents receive no role assignments automatically.

    Returns the number of chunks created.
    """

    if not space_id or not space_id.strip():
        raise ValueError("space_id must not be empty")

    if not classification or not classification.strip():
        raise ValueError("classification must not be empty")

    if limit < 1 or limit > 250:
        raise ValueError("limit must be between 1 and 250")

    client = client or ConfluenceClient()
    total_chunks = 0

    try:
        pages = client.get_pages(
            space_id=space_id,
            limit=limit,
        )

        for page in pages:
            page_id = str(page.get("id") or "").strip()
            title = str(page.get("title") or "").strip()

            if not page_id or not title:
                continue

            content = extract_page_text(page)

            # Do not erase previously indexed content if a response
            # unexpectedly lacks readable page content.
            if not content:
                continue

            document = (
                db.query(Document)
                .filter(
                    Document.source == "confluence",
                    Document.source_id == page_id,
                )
                .first()
            )

            if document is None:
                document = Document(
                    name=title,
                    source="confluence",
                    source_id=page_id,
                    source_url=_page_url(client, page),
                    classification=classification,
                )
                db.add(document)
                db.flush()
            else:
                document.name = title
                document.source_url = _page_url(client, page)
                document.classification = classification

                # Keep document.roles unchanged.

            # Replace chunks for this page.
            document.chunks.clear()
            db.flush()

            for index, chunk_content in enumerate(chunk_text(content)):
                db.add(
                    DocumentChunk(
                        document_id=document.id,
                        content=chunk_content,
                        chunk_index=index,
                    )
                )
                total_chunks += 1

        db.commit()
        return total_chunks

    except Exception:
        db.rollback()
        raise
