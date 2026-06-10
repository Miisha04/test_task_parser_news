
from fastapi import APIRouter, Depends

from app.services import news as news_service


router = APIRouter()

@router.get(
    "/get_news"
)
async def get_news_from(

):
    news = await news_service.get_ria_news()

    return {"news": news}