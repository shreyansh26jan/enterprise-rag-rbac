import os

import httpx
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse

load_dotenv()


class ConfluenceClient:
    """
    Client for interacting with the Confluence REST API.
    """

    def __init__(
        self,
        base_url: str | None = None,
        email: str | None = None,
        api_token: str | None = None,
    ):
        self.base_url = (
            base_url or os.getenv("CONFLUENCE_BASE_URL")
        )
        self.email = (
            email or os.getenv("CONFLUENCE_EMAIL")
        )
        self.api_token = (
            api_token or os.getenv("CONFLUENCE_API_TOKEN")
        )

        if not self.base_url:
            raise ValueError(
                "CONFLUENCE_BASE_URL is not configured"
            )

        if not self.email:
            raise ValueError(
                "CONFLUENCE_EMAIL is not configured"
            )

        if not self.api_token:
            raise ValueError(
                "CONFLUENCE_API_TOKEN is not configured"
            )

        self.base_url = self.base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
        }

    def get_page(
        self,
        page_id: str,
    ) -> dict:
        """
        Retrieve a single Confluence page.
        """

        url = (
            f"{self.base_url}"
            f"/wiki/api/v2/pages/{page_id}"
        )

        # response = httpx.get(
        #     url,
        #     headers=self._headers(),
        #     auth=(self.email, self.api_token),
        #     timeout=30.0,
        # )
        response = httpx.get(
            url,
            headers=self._headers(),
            auth=(self.email, self.api_token),
            params={"body-format": "storage"},
            timeout=30.0,
        )
        response.raise_for_status()

        return response.json()

    def get_pages(
        self,
        space_id: str,
        limit: int = 50,
    ) -> list[dict]:
        """
        Retrieve all pages from a Confluence space.

        Handles cursor-based pagination.
        """

        pages = []

        url = (
            f"{self.base_url}"
            "/wiki/api/v2/pages"
        )

        params = {
            "space-id": space_id,
            "limit": limit,
            "body-format": "storage",
        }

        while url:
            response = httpx.get(
                url,
                headers=self._headers(),
                auth=(self.email, self.api_token),
                params=params,
                timeout=30.0,
            )

            response.raise_for_status()

            data = response.json()

            pages.extend(
                data.get("results", [])
            )

            # next_link = (
            #     data.get("_links", {})
            #     .get("next")
            # )
            next_link = data.get("_links", {}).get("next")

            if next_link:
                next_url = urljoin(url, next_link)

                current_origin = urlparse(self.base_url)
                next_origin = urlparse(next_url)

                if (
                    next_origin.scheme != current_origin.scheme
                    or next_origin.netloc != current_origin.netloc
                ):
                    raise ValueError(
                        "Confluence pagination returned a URL outside "
                        "the configured Confluence host."
                    )

                url = next_url
                params = {}
            else:
                url = None

            # if next_link:
            #     if next_link.startswith("http"):
            #         url = next_link
            #     else:
            #         url = (
            #             f"{self.base_url}"
            #             f"{next_link}"
            #         )

            #     params = {}
            # else:
            #     url = None

        return pages