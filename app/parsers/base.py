from abc import ABC, abstractmethod
from dataclasses import dataclass

from aiohttp import ClientSession


@dataclass
class ParserConfig:
    source_name: str
    base_url: str
    item_selector: str
    fields: dict[str, str]
    timeout: int = 10
    max_retries: int = 3


class BaseParser(ABC):
    source_name: str
    config: ParserConfig

    def __init__(self, config: ParserConfig):
        self.source_name = config.source_name
        self.config = config

    @abstractmethod
    async def parse_short_news(
        self,
        session: ClientSession,
        topic: str | None = None,
    ) -> str:
        pass

    @abstractmethod
    async def parse_extended_news(
        self,
        session: ClientSession,
        url: str,
    ) -> str:
        pass

    @abstractmethod
    def extract_short_news(
        self,
        html: str,
    ) -> list[dict]:
        pass

    @abstractmethod
    def extract_extended_news(
        self,
        html: str,
    ) -> dict:
        pass
