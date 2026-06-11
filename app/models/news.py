from datetime import date, datetime
import enum

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Date,
    DateTime,
    Text,
    Enum as SAEnum,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AdditionStatus(str, enum.Enum):
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    source: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True, index=True)
    publication_date: Mapped[date] = mapped_column(Date, nullable=False)
    announcement: Mapped[str | None] = mapped_column(Text)

    addition_status: Mapped[AdditionStatus] = mapped_column(
        SAEnum(AdditionStatus, values_callable=lambda x: [e.value for e in x]),
        default=AdditionStatus.PENDING,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    addition: Mapped["NewsAddition"] = relationship(back_populates="news", uselist=False)


class NewsAddition(Base):
    __tablename__ = "news_addition"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"), unique=True, nullable=False)

    full_text: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(256))
    images: Mapped[list | None] = mapped_column(JSONB)
    categories: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    key_words: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    summary: Mapped[str | None] = mapped_column(Text)
    views_amount: Mapped[int] = mapped_column(Integer, default=0)
    extra_metadata: Mapped[dict | None] = mapped_column(JSONB)

    news: Mapped["News"] = relationship(back_populates="addition")
