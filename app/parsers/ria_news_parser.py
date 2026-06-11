import asyncio
import json
import re
from collections.abc import Iterable
from urllib.parse import urljoin

from aiohttp import ClientError, ClientSession
from selectolax.parser import HTMLParser

from app.parsers.base import BaseParser, ParserConfig


class RiaNewsParser(BaseParser):
    def __init__(self, config: ParserConfig):
        super().__init__(config)

    async def parse_short_news(
        self,
        session: ClientSession,
        topic: str | None = None,
    ) -> str:
        return await self._fetch(session, self.config.base_url)

    async def parse_extended_news(
        self,
        session: ClientSession,
        url: str,
    ) -> str:
        return await self._fetch(session, url)

    async def _fetch(
        self,
        session: ClientSession,
        url: str,
    ) -> str:
        for attempt in range(self.config.max_retries):
            try:
                async with session.get(url, timeout=self.config.timeout) as response:
                    if response.status == 200:
                        return await response.text()
                    if response.status == 429:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    response.raise_for_status()
            except (asyncio.TimeoutError, ClientError):
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(1)

        raise RuntimeError(f"Failed to parse {url}")

    def extract_short_news(
        self,
        html: str,
    ) -> list[dict]:
        tree = HTMLParser(html)
        results = []

        for item in tree.css(self.config.item_selector):
            news_item = {}

            for field_name, selector in self.config.fields.items():
                if "::attr(" in selector:
                    css_selector, attr = selector.split("::attr(")
                    attr = attr[:-1]
                    node = item.css_first(css_selector)
                    value = node.attributes.get(attr) if node else None

                    if field_name == "url" and value:
                        value = urljoin(self.config.base_url, value)
                else:
                    node = item.css_first(selector)
                    value = node.text(strip=True) if node else None

                news_item[field_name] = value

            if news_item.get("title") and news_item.get("url"):
                results.append(news_item)

        return results

    def extract_extended_news(
        self,
        html: str,
    ) -> dict:
        tree = HTMLParser(html)
        ld_article = _extract_ld_json(tree, "@type", "Article")
        full_text = _extract_full_text(tree)
        author = _extract_author(tree, ld_article)
        images = _extract_images(tree, ld_article, self.config.base_url)
        categories = _extract_categories(tree, ld_article)
        tags = _extract_tags(tree, ld_article)
        key_words = _extract_key_words(tree, ld_article)
        summary = _extract_summary(tree)
        extra_metadata = _extract_extra_metadata(tree, ld_article, html)

        return {
            "full_text": full_text,
            "author": author,
            "images": images,
            "categories": categories,
            "tags": tags,
            "key_words": key_words,
            "summary": summary,
            "views_amount": 0,
            "extra_metadata": extra_metadata,
        }


def _as_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _iter_ld_items(data) -> Iterable[dict]:
    if isinstance(data, dict):
        yield data
        graph = data.get("@graph")
        if graph:
            yield from _iter_ld_items(graph)
    elif isinstance(data, list):
        for item in data:
            yield from _iter_ld_items(item)


def _matches_type(data: dict, article_type: str) -> bool:
    raw_type = data.get("@type")
    if isinstance(raw_type, list):
        return article_type in raw_type
    return raw_type == article_type


def _extract_ld_json(tree: HTMLParser, key: str, value: str) -> dict | None:
    for script in tree.css('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.text())
        except (json.JSONDecodeError, AttributeError):
            continue

        for item in _iter_ld_items(data):
            if key == "@type" and _matches_type(item, value):
                return item
            if item.get(key) == value:
                return item

    return None


def _extract_full_text(tree: HTMLParser) -> str | None:
    selectors = [
        'div.article__block[data-type="text"] div.article__text',
        "div.article__body div.article__text",
        "div.article__text",
    ]

    for selector in selectors:
        blocks = tree.css(selector)
        paragraphs = [block.text(strip=True) for block in blocks if block.text(strip=True)]
        if paragraphs:
            return "\n\n".join(paragraphs)

    return None


def _extract_author(tree: HTMLParser, ld_article: dict | None) -> str | None:
    if ld_article:
        authors = _as_list(ld_article.get("author"))
        for author in authors:
            if isinstance(author, dict) and author.get("@type") == "Person":
                return author.get("name")

        for author in authors:
            if isinstance(author, dict) and author.get("name"):
                return author.get("name")

    meta = tree.css_first('meta[name="analytics:author"]')
    if meta:
        value = meta.attributes.get("content", "").strip()
        return value or None

    return None


def _extract_images(
    tree: HTMLParser,
    ld_article: dict | None,
    base_url: str,
) -> list[dict]:
    images = []
    seen_urls: set[str] = set()

    for selector in ("div.article__announce img", "div.article__body img"):
        for image in tree.css(selector):
            raw_url = image.attributes.get("src", "")
            url = urljoin(base_url, raw_url) if raw_url else ""

            if not url or url in seen_urls:
                continue

            seen_urls.add(url)
            copyright_node = tree.css_first("div.media__copyright-item")
            desc_node = tree.css_first("div.media__description")
            images.append(
                {
                    "url": url,
                    "alt": image.attributes.get("alt", ""),
                    "copyright": copyright_node.text(strip=True) if copyright_node else "",
                    "description": desc_node.text(strip=True) if desc_node else "",
                }
            )

    if not images and ld_article:
        for raw_url in _as_list(ld_article.get("image")):
            if not isinstance(raw_url, str):
                continue

            url = urljoin(base_url, raw_url)
            if url not in seen_urls:
                seen_urls.add(url)
                images.append(
                    {
                        "url": url,
                        "alt": "",
                        "copyright": "",
                        "description": "",
                    }
                )

    return images


def _extract_categories(tree: HTMLParser, ld_article: dict | None) -> list[str]:
    if ld_article:
        categories = [
            item
            for item in _as_list(ld_article.get("articleSection"))
            if isinstance(item, str) and item
        ]
        if categories:
            return categories

    section_meta = tree.css_first('meta[property="article:section"]')
    if section_meta:
        section = section_meta.attributes.get("content", "").strip()
        return [section] if section else []

    return []


def _extract_tags(tree: HTMLParser, ld_article: dict | None) -> list[str]:
    tags = [node.text(strip=True) for node in tree.css("a.article__tags-item")]
    tags = [tag for tag in tags if tag]

    if tags:
        return tags

    return [
        meta.attributes.get("content", "").strip()
        for meta in tree.css('meta[property="article:tag"]')
        if meta.attributes.get("content", "").strip()
    ]


def _extract_key_words(tree: HTMLParser, ld_article: dict | None) -> list[str]:
    raw_keywords = ld_article.get("keywords") if ld_article else None

    if isinstance(raw_keywords, str):
        key_words = [word.strip() for word in raw_keywords.split(",") if word.strip()]
        if key_words:
            return key_words

    if isinstance(raw_keywords, list):
        key_words = [word for word in raw_keywords if isinstance(word, str) and word]
        if key_words:
            return key_words

    meta = tree.css_first('meta[name="analytics:keyw"]')
    if meta:
        return [
            word.strip()
            for word in meta.attributes.get("content", "").split(",")
            if word.strip()
        ]

    return []


def _extract_summary(tree: HTMLParser) -> str | None:
    items = tree.css("ul.article__summary-list li")
    if items:
        summary = " ".join(item.text(strip=True) for item in items if item.text(strip=True))
        if summary:
            return summary

    og_desc = tree.css_first('meta[property="og:description"]')
    if og_desc:
        return og_desc.attributes.get("content", "").strip() or None

    return None


def _extract_extra_metadata(
    tree: HTMLParser,
    ld_article: dict | None,
    html: str,
) -> dict:
    meta: dict = {}

    id_match = re.search(r"GLOBAL\.article\.id\s*=\s*(\d+)", html)
    if id_match:
        meta["article_id"] = int(id_match.group(1))

    canonical = tree.css_first('link[rel="canonical"]')
    if canonical:
        meta["url"] = canonical.attributes.get("href", "")

    if ld_article:
        meta["date_published"] = (ld_article.get("datePublished") or "").strip()
        meta["date_modified"] = (ld_article.get("dateModified") or "").strip()
        meta["genre"] = ld_article.get("genre", "")
        meta["language"] = ld_article.get("inLanguage", "")

    rubric_match = re.search(r"'page_rubric'\s*:\s*'([^']+)'", html)
    if rubric_match:
        meta["rubric"] = rubric_match.group(1)

    length_match = re.search(r"'article_length'\s*:\s*'(\d+)'", html)
    if length_match:
        meta["article_length_chars"] = int(length_match.group(1))

    return meta
