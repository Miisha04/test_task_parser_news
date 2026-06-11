from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.news import AdditionStatus, News, NewsAddition


async def get_news_by_url(
    db: AsyncSession,
    url: str,
) -> News | None:
    result = await db.execute(select(News).where(News.url == url))
    return result.scalar_one_or_none()


async def get_news_by_urls(
    db: AsyncSession,
    urls: list[str],
) -> list[News]:
    if not urls:
        return []

    result = await db.execute(select(News).where(News.url.in_(urls)))
    return result.scalars().all()


def _apply_news_filters(
    query,
    source: str | None = None,
    status: AdditionStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    has_addition: bool | None = None,
):
    if source:
        query = query.where(News.source == source)

    if status:
        query = query.where(News.addition_status == status)

    if date_from:
        query = query.where(News.publication_date >= date_from)

    if date_to:
        query = query.where(News.publication_date <= date_to)

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                News.title.ilike(pattern),
                News.announcement.ilike(pattern),
            )
        )

    if has_addition is True:
        query = query.where(News.addition.has())

    if has_addition is False:
        query = query.where(~News.addition.has())

    return query


async def get_news(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    source: str | None = None,
    status: AdditionStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    has_addition: bool | None = None,
    include_addition: bool = False,
) -> list[News]:
    query = select(News)

    if include_addition:
        query = query.options(selectinload(News.addition))

    query = _apply_news_filters(
        query,
        source=source,
        status=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
        has_addition=has_addition,
    )

    result = await db.execute(
        query
        .order_by(News.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_all_news_short(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    source: str | None = None,
    status: AdditionStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
) -> list[News]:
    return await get_news(
        db,
        limit=limit,
        offset=offset,
        source=source,
        status=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
        include_addition=False,
    )


async def get_all_news_extended(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    source: str | None = None,
    status: AdditionStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    has_addition: bool | None = None,
) -> list[News]:
    return await get_news(
        db,
        limit=limit,
        offset=offset,
        source=source,
        status=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
        has_addition=has_addition,
        include_addition=True,
    )


async def get_news_by_id(
    db: AsyncSession,
    news_id: int,
) -> News | None:
    result = await db.execute(
        select(News)
        .where(News.id == news_id)
        .options(selectinload(News.addition))
    )
    return result.scalar_one_or_none()


async def save_short_news(
    db: AsyncSession,
    news: list[News],
) -> None:
    db.add_all(news)


async def save_extended_news(
    db: AsyncSession,
    news_id: int,
    extended_data: dict,
) -> NewsAddition:
    result = await db.execute(
        select(NewsAddition).where(NewsAddition.news_id == news_id)
    )
    news_addition = result.scalar_one_or_none()

    if news_addition:
        for field, value in extended_data.items():
            setattr(news_addition, field, value)
        return news_addition

    news_addition = NewsAddition(news_id=news_id, **extended_data)
    db.add(news_addition)
    return news_addition


async def update_news_status(
    db: AsyncSession,
    news_id: int,
    status: AdditionStatus,
) -> None:
    news = await db.get(News, news_id)
    if news:
        news.addition_status = status


async def get_news_by_status(
    db: AsyncSession,
    source_name: str,
    status: AdditionStatus,
    limit: int | None = None,
) -> list[News]:
    query = (
        select(News)
        .where(News.source == source_name)
        .where(News.addition_status == status)
        .order_by(News.created_at.desc())
    )

    if limit:
        query = query.limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
