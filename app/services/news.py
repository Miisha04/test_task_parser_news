from aiohttp import ClientSession

from app.settings import get_settings
from app.parsers.ria_news_parser import RiaNewsParser

settins = get_settings()


async def get_ria_news():
    ria_client = RiaNewsParser()
    session = ClientSession()

    result = await ria_client.parse(
        "politics", 
        session
    )

    news = RiaNewsParser.extract_news(
        html=result,
        item_selector=".cell-list__item",
        fields={
            "title": ".cell-list__item-title",
            "url": "a::attr(href)",
            "date": ".cell-info__date",
        },
    )

    await session.close()
    return news
