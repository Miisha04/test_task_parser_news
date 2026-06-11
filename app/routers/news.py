from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_http_client
from app.models.news import AdditionStatus
from app.parsers.factory import ParserFactory
from app.schemas.news import NewsExtendedResponse, NewsShortResponse
from app.services import news as news_service


router = APIRouter(prefix="/news", tags=["news"])


@router.post(
    "/load",
    status_code=status.HTTP_200_OK,
)
async def load_news(
    db: AsyncSession = Depends(get_db),
    http_client=Depends(get_http_client),
    source: str | None = Query(None),
    extended_limit: int | None = Query(10, ge=1, le=100),
):
    sources = [source] if source else None
    return await news_service.load_all_news(db, http_client, sources, extended_limit)


@router.get(
    "/load",
    status_code=status.HTTP_200_OK,
)
async def load_news_legacy(
    db: AsyncSession = Depends(get_db),
    http_client=Depends(get_http_client),
    source: str | None = Query(None),
):
    return await news_service.load_short_news(db, http_client, source)


@router.post(
    "/load/short",
    status_code=status.HTTP_200_OK,
)
async def load_short_news(
    db: AsyncSession = Depends(get_db),
    http_client=Depends(get_http_client),
    source: str | None = Query(None),
):
    return await news_service.load_short_news(db, http_client, source)


@router.post(
    "/load/extended",
    status_code=status.HTTP_200_OK,
)
async def load_extended_news(
    db: AsyncSession = Depends(get_db),
    http_client=Depends(get_http_client),
    news_id: int | None = Query(None, ge=1),
    source: str | None = Query(None),
    limit: int | None = Query(10, ge=1, le=100),
    status_filter: AdditionStatus = Query(AdditionStatus.PENDING, alias="status"),
):
    news = await news_service.load_extended_news(
        db,
        http_client,
        news_id=news_id,
        source=source,
        limit=limit,
        status_filter=status_filter,
    )

    if news_id is not None and not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"News with id {news_id} not found",
        )

    return news


@router.get(
    "/sources",
    status_code=status.HTTP_200_OK,
)
async def get_available_sources():
    return {"sources": ParserFactory.get_available_sources()}


@router.get(
    "/short",
    status_code=status.HTTP_200_OK,
    response_model=list[NewsShortResponse],
)
async def get_short_news(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    source: str | None = Query(None),
    status_filter: AdditionStatus | None = Query(None, alias="status"),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    search: str | None = Query(None, min_length=1),
):
    return await news_service.get_short_news(
        db,
        limit=limit,
        offset=offset,
        source=source,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )


@router.get(
    "/extended",
    status_code=status.HTTP_200_OK,
    response_model=list[NewsExtendedResponse],
)
async def get_extended_news(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    source: str | None = Query(None),
    status_filter: AdditionStatus | None = Query(None, alias="status"),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    search: str | None = Query(None, min_length=1),
    has_addition: bool | None = Query(None),
):
    return await news_service.get_extended_news(
        db,
        limit=limit,
        offset=offset,
        source=source,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        search=search,
        has_addition=has_addition,
    )


@router.get(
    "/{news_id}",
    status_code=status.HTTP_200_OK,
    response_model=NewsExtendedResponse,
)
async def get_full_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
):
    news = await news_service.get_full_news(db, news_id)

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"News with id {news_id} not found",
        )

    return news
