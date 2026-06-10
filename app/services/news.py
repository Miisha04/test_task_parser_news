from datetime import datetime, timezone

from aiohttp import ClientSession

from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import get_settings
from app.parsers.ria_news_parser import RiaNewsParser
from app.schemas.news import NewsShortCreate, NewsShortResponse
from app.repositories import news as news_repos
from app.models.news import News, AdditionStatus

settins = get_settings()


async def get_ria_news():
    ria_client = RiaNewsParser()
    session = ClientSession()

    async with ClientSession() as session:
        result = await ria_client.parse("politics", session)

    news = RiaNewsParser.extract_news(
        html=result,
        item_selector=".cell-list__item",
        fields={
            "title": ".cell-list__item-title",
            "url": "a::attr(href)",
            "date": ".cell-info__date",
        },
    )

    return news


async def load_ria_news(
    db: AsyncSession
):
    ria_client = RiaNewsParser()
    session = ClientSession()

    async with ClientSession() as session:
        result = await ria_client.parse(topic=None, session=session)

    news = RiaNewsParser.extract_news(
        html=result,
        item_selector=".cell-list__item",
        fields={
            "title": ".cell-list__item-title",
            "url": "a::attr(href)",
            "time": (".cell-info__date"),
        },
    )

    for n in news:
        n["addition_status"] = AdditionStatus.PENDING.value
        n["source"] = "ria_news"
        n["publication_date"] = datetime.now(tz=timezone.utc)
        n["announcement"] = None

    news_models = [
        News(**NewsShortCreate.model_validate(n).model_dump())
        for n in news
    ]

    try:
        await news_repos.save_short_news(db, news_models)
        await db.commit()
        for n in news_models:
            await db.refresh(n)
    except Exception:
        await db.rollback()
        raise


    return [NewsShortResponse.model_validate(n) for n in news_models]



