from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import News


async def save_short_news(
    db: AsyncSession,
    news: list[News]
) -> None:
    db.add_all(news)