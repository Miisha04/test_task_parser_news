
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import news as news_service
from app.schemas.news import NewsShortResponse
from app.database import get_db


router = APIRouter()


@router.get(
    "/load_short_news",
    status_code=status.HTTP_200_OK
)
async def load_short_news(
    db: AsyncSession = Depends(get_db) 
) -> list[NewsShortResponse]:
    return await news_service.load_ria_news(db)


@router.get(
    "/get_news"
)
async def get_news_from(

):
    news = await news_service.get_ria_news()

    return {"news": news}