from datetime import date

from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from app.loaders.news_loader import NewsLoader, load_all_news_multi_source
from app.models.news import AdditionStatus
from app.parsers.factory import ParserFactory
from app.repositories import news as news_repos
from app.schemas.news import NewsExtendedResponse, NewsShortResponse


async def load_all_news(
    db: AsyncSession,
    http_client: ClientSession,
    sources: list[str] | None = None,
    extended_limit: int | None = 10,
) -> dict:
    return await load_all_news_multi_source(db, http_client, sources, extended_limit)


async def load_short_news(
    db: AsyncSession,
    http_client: ClientSession,
    source: str | None = None,
) -> dict | list[NewsShortResponse]:
    loader = NewsLoader(db, http_client)

    if source:
        return await loader.load_short_news_from_source(source)

    return await loader.load_short_news_from_all_sources()


async def load_extended_news(
    db: AsyncSession,
    http_client: ClientSession,
    news_id: int | None = None,
    source: str | None = None,
    limit: int | None = 10,
    status_filter: AdditionStatus = AdditionStatus.PENDING,
) -> dict | NewsExtendedResponse | None:
    loader = NewsLoader(db, http_client)

    if news_id is not None:
        news = await loader.load_extended_news_for_single_news(news_id, source)
        return NewsExtendedResponse.model_validate(news) if news else None

    sources = [source] if source else None
    selected_sources = sources or []

    if not selected_sources:
        selected_sources = ParserFactory.get_available_sources()

    result = {}

    for source_name in selected_sources:
        result[source_name] = await loader.load_extended_news_for_all(
            source_name,
            limit=limit,
            status_filter=status_filter,
        )

    return result


async def get_short_news(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    source: str | None = None,
    status: AdditionStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
) -> list[NewsShortResponse]:
    news = await news_repos.get_all_news_short(
        db,
        limit=limit,
        offset=offset,
        source=source,
        status=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    return [NewsShortResponse.model_validate(item) for item in news]


async def get_extended_news(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    source: str | None = None,
    status: AdditionStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    has_addition: bool | None = None,
) -> list[NewsExtendedResponse]:
    news = await news_repos.get_all_news_extended(
        db,
        limit=limit,
        offset=offset,
        source=source,
        status=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
        has_addition=has_addition,
    )
    return [NewsExtendedResponse.model_validate(item) for item in news]


async def get_full_news(
    db: AsyncSession,
    news_id: int,
) -> NewsExtendedResponse | None:
    news = await news_repos.get_news_by_id(db, news_id)

    if not news:
        return None

    return NewsExtendedResponse.model_validate(news)
