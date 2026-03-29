from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass

import httpx

from src import config

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WikiSummary:
    title: str
    extract: str
    article_url: str
    image_url: str | None


class WikipediaClient:
    def __init__(self, lang: str = "en", timeout: float = 15.0) -> None:
        self._lang = lang
        self._timeout = timeout
        self._headers = {
            "User-Agent": config.WIKIPEDIA_USER_AGENT,
            "Accept": "application/json",
        }
        self._api = f"https://{lang}.wikipedia.org/w/api.php"
        self._rest_base = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary"

    async def _opensearch_title(self, search: str) -> str | None:
        params = {
            "action": "opensearch",
            "search": search,
            "limit": 1,
            "namespace": 0,
            "format": "json",
        }
        async with httpx.AsyncClient(timeout=self._timeout, headers=self._headers) as client:
            r = await client.get(self._api, params=params)
            r.raise_for_status()
            data = r.json()
        if not isinstance(data, list) or len(data) < 2:
            return None
        titles = data[1]
        if not titles:
            return None
        return str(titles[0])

    async def summary_for_place(self, place: str) -> WikiSummary | None:
        query = place.strip()
        if not query:
            return None
        title = await self._opensearch_title(query)
        if not title:
            return None
        safe = title.replace(" ", "_")
        url = f"{self._rest_base}/{urllib.parse.quote(safe, safe='')}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(url, headers=self._headers)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            payload = r.json()

        page_type = payload.get("type")
        if page_type in ("disambiguation", "redirect", "mainpage"):
            return None

        extract = str(payload.get("extract", "")).strip()
        title_out = str(payload.get("title", title))
        content_urls = payload.get("content_urls") or {}
        desktop = content_urls.get("desktop") or {}
        article_url = str(desktop.get("page", f"https://{self._lang}.wikipedia.org/wiki/{safe}"))

        image_url: str | None = None
        original = payload.get("originalimage") or {}
        if isinstance(original, dict) and original.get("source"):
            image_url = str(original["source"])
        else:
            thumb = payload.get("thumbnail") or {}
            if isinstance(thumb, dict) and thumb.get("source"):
                image_url = str(thumb["source"])

        if not extract and not image_url:
            logger.info("Wikipedia page has no extract or image: %s", title_out)
            return None

        return WikiSummary(
            title=title_out,
            extract=extract or "(No summary text available.)",
            article_url=article_url,
            image_url=image_url,
        )
