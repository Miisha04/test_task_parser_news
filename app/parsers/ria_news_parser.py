from aiohttp import ClientSession
from urllib.parse import urljoin
from selectolax.parser import HTMLParser


from app.parsers.base import BaseParser
from app.settings import get_settings

settings = get_settings()

class RiaNewsParser(BaseParser):
    source_name = "ria_news"
    
    base_url = settings.ria_news_url

    async def parse(self, topic: str, session: ClientSession):
        try:
            response = await session.get(self.base_url)
            
            if response.status != 200:
                raise
            return await response.text()
        
        except Exception as e:
            raise 

    @staticmethod
    def extract_news(
        html: str,
        item_selector: str,
        fields: dict[str, str],
        base_url: str | None = None,
    ) -> list[dict]:
        """
        Универсальный parser для новостей.

        Args:
            html: html страницы
            item_selector: css selector карточки новости
            fields: mapping полей

            Пример:
            {
                "title": ".title",
                "url": "a::attr(href)",
                "date": ".date"
            }

            base_url: для относительных ссылок

        Returns:
            list[dict]
        """

        tree = HTMLParser(html)
        results = []

        for item in tree.css(item_selector):
            news_item = {}

            for field_name, selector in fields.items():

                if "::attr(" in selector:
                    css_selector, attr = selector.split("::attr(")
                    attr = attr[:-1]

                    node = item.css_first(css_selector)

                    value = None
                    if node:
                        value = node.attributes.get(attr)

                        if (
                            field_name == "url"
                            and value
                            and base_url
                        ):
                            value = urljoin(base_url, value)

                else:
                    node = item.css_first(selector)
                    value = (
                        node.text(strip=True)
                        if node
                        else None
                    )

                news_item[field_name] = value

            # фильтр пустых
            if any(news_item.values()):
                results.append(news_item)

        return results