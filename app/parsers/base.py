from abc import ABC, abstractmethod

class BaseParser(ABC):

    source_name: str

    # @abstractmethod
    # async def collect(self) -> list[dict]:
    #     pass