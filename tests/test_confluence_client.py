
import httpx
import pytest

from unittest.mock import Mock, patch

from app.ingestion.confluence_client import ConfluenceClient


@pytest.fixture
def client():
    return ConfluenceClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token",
    )


def test_missing_base_url():
    with patch.dict(
        "os.environ",
        {
            "CONFLUENCE_BASE_URL": "",
            "CONFLUENCE_EMAIL": "test@example.com",
            "CONFLUENCE_API_TOKEN": "test-token",
        },
        clear=False,
    ):
        with pytest.raises(
            ValueError,
            match="CONFLUENCE_BASE_URL",
        ):
            ConfluenceClient()


def test_missing_email():
    with patch.dict(
        "os.environ",
        {
            "CONFLUENCE_BASE_URL": "https://example.atlassian.net",
            "CONFLUENCE_EMAIL": "",
            "CONFLUENCE_API_TOKEN": "test-token",
        },
        clear=False,
    ):
        with pytest.raises(
            ValueError,
            match="CONFLUENCE_EMAIL",
        ):
            ConfluenceClient()


def test_missing_api_token():
    with patch.dict(
        "os.environ",
        {
            "CONFLUENCE_BASE_URL": "https://example.atlassian.net",
            "CONFLUENCE_EMAIL": "test@example.com",
            "CONFLUENCE_API_TOKEN": "",
        },
        clear=False,
    ):
        with pytest.raises(
            ValueError,
            match="CONFLUENCE_API_TOKEN",
        ):
            ConfluenceClient()


@patch("app.ingestion.confluence_client.httpx.get")
def test_get_page_success(mock_get, client):
    mock_response = Mock()
    mock_response.json.return_value = {
        "id": "123",
        "title": "Engineering Architecture",
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    page = client.get_page("123")

    assert page["id"] == "123"
    assert page["title"] == "Engineering Architecture"

    mock_get.assert_called_once_with(
        "https://example.atlassian.net/wiki/api/v2/pages/123",
        headers={"Accept": "application/json"},
        auth=("test@example.com", "test-token"),
        params={"body-format": "storage"},
        timeout=30.0,
    )


@patch("app.ingestion.confluence_client.httpx.get")
def test_get_pages_single_page(mock_get, client):
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {"id": "1", "title": "Page One"},
            {"id": "2", "title": "Page Two"},
        ],
        "_links": {},
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    pages = client.get_pages(space_id="123")

    assert len(pages) == 2
    assert pages[0]["title"] == "Page One"
    assert pages[1]["title"] == "Page Two"

    mock_get.assert_called_once_with(
        "https://example.atlassian.net/wiki/api/v2/pages",
        headers={"Accept": "application/json"},
        auth=("test@example.com", "test-token"),
        # params={"space-id": "123", "limit": 50},
                
        params={
            "space-id": "123",
            "limit": 50,
            "body-format": "storage",
        },
        timeout=30.0,
    )


@patch("app.ingestion.confluence_client.httpx.get")
def test_get_pages_pagination(mock_get, client):
    first_response = Mock()
    first_response.json.return_value = {
        "results": [{"id": "1", "title": "Page One"}],
        "_links": {
            "next": "/wiki/api/v2/pages?cursor=next-page"
        },
    }
    first_response.raise_for_status.return_value = None

    second_response = Mock()
    second_response.json.return_value = {
        "results": [{"id": "2", "title": "Page Two"}],
        "_links": {},
    }
    second_response.raise_for_status.return_value = None

    mock_get.side_effect = [first_response, second_response]

    pages = client.get_pages(space_id="123")

    assert len(pages) == 2
    assert [page["id"] for page in pages] == ["1", "2"]

    assert mock_get.call_count == 2

    second_call = mock_get.call_args_list[1]

    assert second_call.args[0] == (
        "https://example.atlassian.net"
        "/wiki/api/v2/pages?cursor=next-page"
    )
    assert second_call.kwargs["params"] == {}


@patch("app.ingestion.confluence_client.httpx.get")
def test_get_pages_absolute_next_url(mock_get, client):
    first_response = Mock()
    first_response.json.return_value = {
        "results": [{"id": "1", "title": "Page One"}],
        "_links": {
            "next": (
                "https://example.atlassian.net"
                "/wiki/api/v2/pages?cursor=next-page"
            )
        },
    }
    first_response.raise_for_status.return_value = None

    second_response = Mock()
    second_response.json.return_value = {
        "results": [{"id": "2", "title": "Page Two"}],
        "_links": {},
    }
    second_response.raise_for_status.return_value = None

    mock_get.side_effect = [first_response, second_response]

    pages = client.get_pages(space_id="123")

    assert len(pages) == 2
    assert mock_get.call_count == 2

    assert mock_get.call_args_list[1].args[0] == (
        "https://example.atlassian.net"
        "/wiki/api/v2/pages?cursor=next-page"
    )


@patch("app.ingestion.confluence_client.httpx.get")
def test_get_page_http_error(mock_get, client):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = (
        httpx.HTTPStatusError(
            "Not found",
            request=httpx.Request(
                "GET",
                "https://example.atlassian.net/wiki/api/v2/pages/999",
            ),
            response=httpx.Response(
                404,
                request=httpx.Request(
                    "GET",
                    "https://example.atlassian.net/wiki/api/v2/pages/999",
                ),
            ),
        )
    )
    mock_get.return_value = mock_response

    with pytest.raises(httpx.HTTPStatusError):
        client.get_page("999")


@patch("app.ingestion.confluence_client.httpx.get")
def test_get_pages_http_error(mock_get, client):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = (
        httpx.HTTPStatusError(
            "Forbidden",
            request=httpx.Request(
                "GET",
                "https://example.atlassian.net/wiki/api/v2/pages",
            ),
            response=httpx.Response(
                403,
                request=httpx.Request(
                    "GET",
                    "https://example.atlassian.net/wiki/api/v2/pages",
                ),
            ),
        )
    )
    mock_get.return_value = mock_response

    with pytest.raises(httpx.HTTPStatusError):
        client.get_pages(space_id="123")


@patch("app.ingestion.confluence_client.httpx.get")
def test_get_pages_empty_results(mock_get, client):
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [],
        "_links": {},
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    pages = client.get_pages(space_id="123")

    assert pages == []
    mock_get.assert_called_once()


# def test_get_pages_rejects_external_pagination_url(confluence_client):
#     from unittest.mock import patch

#     import httpx
#     import pytest

#     response = httpx.Response(
#         200,
#         json={
#             "results": [],
#             "_links": {
#                 "next": "https://attacker.example/steal"
#             },
#         },
#         request=httpx.Request(
#             "GET",
#             f"{confluence_client.base_url}/wiki/api/v2/pages",
#         ),
#     )

#     with patch(
#         "app.ingestion.confluence_client.httpx.get",
#         return_value=response,
#     ) as mock_get:
#         with pytest.raises(ValueError, match="outside"):
#             confluence_client.get_pages(space_id="123")

#     assert mock_get.call_count == 1