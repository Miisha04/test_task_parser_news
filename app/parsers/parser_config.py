from app.parsers.base import ParserConfig


RIA_NEWS_CONFIG = ParserConfig(
    source_name="ria_news",
    base_url="https://ria.ru",
    item_selector=".cell-list__item",
    fields={
        "title": ".cell-list__item-title",
        "url": "a.cell-list__item-link::attr(href)",
    },
    timeout=10,
    max_retries=3,
)

PARSERS_REGISTRY = {
    "ria_news": RIA_NEWS_CONFIG,
}


def get_parser_config(source_name: str) -> ParserConfig | None:
    return PARSERS_REGISTRY.get(source_name)


def register_parser(config: ParserConfig) -> None:
    PARSERS_REGISTRY[config.source_name] = config


def get_all_sources() -> list[str]:
    return list(PARSERS_REGISTRY.keys())
