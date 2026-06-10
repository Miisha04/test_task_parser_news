from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.news import AdditionStatus


class NewsShortBase(BaseModel):
    title: str
    source: str
    publication_date: datetime
    announcement: str | None
    addition_status: AdditionStatus

    model_config = ConfigDict(from_attributes=True)

class NewsShortCreate(NewsShortBase):
    pass

class NewsShortResponse(NewsShortBase):
    id: int


class NewsAdditionResponse(BaseModel):
    full_text: str | None
    author: str | None
    images: list[dict] | None
    categories: list[str] | None
    tags: list[str] | None
    key_words: list[str] | None
    summary: str | None
    views_amount: int
    extra_metadata: dict | None


class NewsDetailsResponse(BaseModel):
    id: int
    title: str
    source: str
    publication_date: datetime
    announcement: str | None
    addition_status: AdditionStatus
    addition: NewsAdditionResponse | None
