from datetime import datetime, timezone

from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import AdditionStatus, News
from app.parsers.factory import ParserFactory
from app.repositories import news as news_repos
from app.schemas.news import NewsShortCreate, NewsShortResponse


class NewsLoader:
    def __init__(self, db: AsyncSession, http_client: ClientSession):
        self.db = db
        self.http_client = http_client

    async def load_short_news_from_source(
        self,
        source_name: str,
    ) -> list[NewsShortResponse]:
        parser = ParserFactory.create(source_name)

        html = await parser.parse_short_news(self.http_client)
        news_data = parser.extract_short_news(html)

        urls = [n.get("url") for n in news_data if n.get("url")]
        existing_news = await news_repos.get_news_by_urls(self.db, urls)
        existing_urls = {n.url for n in existing_news}
        new_news = [n for n in news_data if n.get("url") not in existing_urls]

        for item in new_news:
            item["addition_status"] = AdditionStatus.PENDING.value
            item["source"] = source_name
            item["publication_date"] = datetime.now(tz=timezone.utc).date()
            item["announcement"] = item.get("announcement")

        news_models = [
            News(**NewsShortCreate.model_validate(item).model_dump())
            for item in new_news
        ]

        if news_models:
            await news_repos.save_short_news(self.db, news_models)
            await self.db.commit()
            for item in news_models:
                await self.db.refresh(item)

        return [NewsShortResponse.model_validate(item) for item in news_models]

    async def load_short_news_from_all_sources(
        self,
        sources: list[str] | None = None,
    ) -> dict[str, list[NewsShortResponse] | dict[str, str]]:
        if sources is None:
            sources = ParserFactory.get_available_sources()

        results = {}

        for source in sources:
            try:
                results[source] = await self.load_short_news_from_source(source)
            except Exception as exc:
                await self.db.rollback()
                results[source] = {"error": str(exc)}

        return results

    async def load_extended_news_for_single_news(
        self,
        news_id: int,
        source_name: str | None = None,
    ) -> News | None:
        news = await news_repos.get_news_by_id(self.db, news_id)

        if not news:
            return None

        parser = ParserFactory.create(source_name or news.source)

        try:
            html = await parser.parse_extended_news(self.http_client, news.url)
            extended_data = parser.extract_extended_news(html)
            await news_repos.save_extended_news(self.db, news_id, extended_data)
            await news_repos.update_news_status(self.db, news_id, AdditionStatus.DONE)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            await news_repos.update_news_status(self.db, news_id, AdditionStatus.FAILED)
            await self.db.commit()
            raise

        refreshed_news = await news_repos.get_news_by_id(self.db, news_id)
        return refreshed_news

    async def load_extended_news_for_all(
        self,
        source_name: str,
        limit: int | None = None,
        status_filter: AdditionStatus = AdditionStatus.PENDING,
    ) -> dict[str, int]:
        news_items = await news_repos.get_news_by_status(
            self.db,
            source_name,
            status_filter,
            limit,
        )
        loaded = 0
        failed = 0

        for news_item in news_items:
            try:
                await self.load_extended_news_for_single_news(news_item.id, source_name)
                loaded += 1
            except Exception:
                failed += 1

        return {"loaded": loaded, "failed": failed}


async def load_all_news_multi_source(
    db: AsyncSession,
    http_client: ClientSession,
    sources: list[str] | None = None,
    extended_limit: int | None = 10,
) -> dict:
    loader = NewsLoader(db, http_client)
    selected_sources = sources or ParserFactory.get_available_sources()
    short_news_by_source = await loader.load_short_news_from_all_sources(selected_sources)
    extended_by_source = {}

    for source_name in selected_sources:
        extended_by_source[source_name] = await loader.load_extended_news_for_all(
            source_name,
            limit=extended_limit,
        )

    short_count = sum(
        len(news_items) if isinstance(news_items, list) else 0
        for news_items in short_news_by_source.values()
    )

    return {
        "short_news_count": short_count,
        "short": short_news_by_source,
        "extended": extended_by_source,
    }
