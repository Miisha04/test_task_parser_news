from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.news import AdditionStatus


class NewsShortBase(BaseModel):
    title: str
    source: str
    publication_date: date
    announcement: str | None
    addition_status: AdditionStatus
    url: str

    model_config = ConfigDict(from_attributes=True)


class NewsShortCreate(NewsShortBase):
    pass


class NewsShortResponse(NewsShortBase):
    id: int


class NewsAdditionBase(BaseModel):
    full_text: str | None = None
    author: str | None = None
    images: list[dict] | None = None
    categories: list[str] | None = None
    tags: list[str] | None = None
    key_words: list[str] | None = None
    summary: str | None = None
    views_amount: int = 0
    extra_metadata: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class NewsExtendedBase(BaseModel):
    title: str
    source: str
    url: str
    publication_date: date
    announcement: str | None
    addition_status: AdditionStatus
    addition: NewsAdditionBase | None

    model_config = ConfigDict(from_attributes=True)


class NewsExtendedCreate(NewsAdditionBase):
    pass


class NewsExtendedResponse(NewsExtendedBase):
    id: int

