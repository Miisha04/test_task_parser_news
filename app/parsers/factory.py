from app.parsers.base import BaseParser, ParserConfig
from app.parsers.parser_config import get_all_sources, get_parser_config, register_parser
from app.parsers.ria_news_parser import RiaNewsParser


class ParserFactory:
    _parsers = {
        "ria_news": RiaNewsParser,
    }

    @classmethod
    def create(cls, source_name: str) -> BaseParser:
        parser_class = cls._parsers.get(source_name)
        if not parser_class:
            raise ValueError(f"Unknown parser: {source_name}")

        config = get_parser_config(source_name)
        if not config:
            raise ValueError(f"No config for parser: {source_name}")

        return parser_class(config)

    @classmethod
    def register(
        cls,
        source_name: str,
        parser_class: type[BaseParser],
        config: ParserConfig,
    ) -> None:
        if not issubclass(parser_class, BaseParser):
            raise TypeError(f"{parser_class} must inherit from BaseParser")

        cls._parsers[source_name] = parser_class
        register_parser(config)

    @classmethod
    def get_available_sources(cls) -> list[str]:
        return [
            source
            for source in get_all_sources()
            if source in cls._parsers
        ]
